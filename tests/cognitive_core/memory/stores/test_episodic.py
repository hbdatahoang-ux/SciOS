from __future__ import annotations

from datetime import datetime, timezone

import pytest

from scios.cognitive_core.memory.core import (
    MemoryRecord,
    MemoryStore,
)
from scios.cognitive_core.memory.stores.episodic import EpisodicMemory


@pytest.fixture
def store() -> EpisodicMemory:
    return EpisodicMemory()


@pytest.fixture
def record() -> MemoryRecord:
    return MemoryRecord(
        content="User completed an experiment.",
        metadata={"session": "exp-001"},
        created_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )


def test_subclasses_memory_store() -> None:
    assert issubclass(EpisodicMemory, MemoryStore)


def test_is_concrete() -> None:
    store = EpisodicMemory()
    assert isinstance(store, EpisodicMemory)


def test_default_name() -> None:
    store = EpisodicMemory()
    assert store.name == "EpisodicMemory"


def test_custom_name() -> None:
    store = EpisodicMemory(name="ExperimentEpisodes")
    assert store.name == "ExperimentEpisodes"


def test_initial_count_is_zero() -> None:
    store = EpisodicMemory()
    assert store.count() == 0


def test_initial_all_is_empty_tuple() -> None:
    store = EpisodicMemory()
    assert store.all() == ()
    assert isinstance(store.all(), tuple)


def test_store_returns_same_record(
    store: EpisodicMemory,
    record: MemoryRecord,
) -> None:
    stored = store.store(record)

    assert stored is record


def test_store_and_get(
    store: EpisodicMemory,
    record: MemoryRecord,
) -> None:
    store.store(record)

    result = store.get(record.id)

    assert result is record


def test_get_missing_returns_none(
    store: EpisodicMemory,
) -> None:
    assert store.get("missing-id") is None


def test_count_after_store(
    store: EpisodicMemory,
    record: MemoryRecord,
) -> None:
    store.store(record)

    assert store.count() == 1


def test_all_returns_tuple(
    store: EpisodicMemory,
    record: MemoryRecord,
) -> None:
    store.store(record)

    result = store.all()

    assert isinstance(result, tuple)
    assert result == (record,)


def test_all_preserves_insertion_order(
    store: EpisodicMemory,
) -> None:
    records = [
        MemoryRecord(content="event-1"),
        MemoryRecord(content="event-2"),
        MemoryRecord(content="event-3"),
    ]

    for item in records:
        store.store(item)

    assert store.all() == tuple(records)


def test_multiple_records_are_stored(
    store: EpisodicMemory,
) -> None:
    records = [MemoryRecord(content=f"event-{i}") for i in range(5)]

    for record in records:
        store.store(record)

    assert store.count() == 5
    assert store.all() == tuple(records)


def test_delete_existing_record(
    store: EpisodicMemory,
    record: MemoryRecord,
) -> None:
    store.store(record)

    assert store.delete(record.id) is True
    assert store.count() == 0
    assert store.get(record.id) is None


def test_delete_missing_record_returns_false(
    store: EpisodicMemory,
) -> None:
    assert store.delete("missing-id") is False


def test_delete_one_record_preserves_others(
    store: EpisodicMemory,
) -> None:
    first = MemoryRecord(content="event-1")
    second = MemoryRecord(content="event-2")
    third = MemoryRecord(content="event-3")

    store.store(first)
    store.store(second)
    store.store(third)

    assert store.delete(second.id) is True

    assert store.count() == 2
    assert store.all() == (first, third)


def test_clear_removes_all_records(
    store: EpisodicMemory,
) -> None:
    records = [MemoryRecord(content=f"event-{i}") for i in range(3)]

    for record in records:
        store.store(record)

    store.clear()

    assert store.count() == 0
    assert store.all() == ()


def test_clear_is_idempotent(
    store: EpisodicMemory,
) -> None:
    store.clear()
    store.clear()

    assert store.count() == 0
    assert store.all() == ()


def test_store_after_clear(
    store: EpisodicMemory,
    record: MemoryRecord,
) -> None:
    store.store(record)
    store.clear()

    stored = store.store(record)

    assert stored is record
    assert store.count() == 1
    assert store.get(record.id) is record


def test_duplicate_id_replaces_existing_record(
    store: EpisodicMemory,
) -> None:
    first = MemoryRecord(
        id="episode-1",
        content="first event",
    )
    second = MemoryRecord(
        id="episode-1",
        content="updated event",
    )

    store.store(first)
    result = store.store(second)

    assert result is second
    assert store.count() == 1
    assert store.get("episode-1") is second
    assert store.all() == (second,)


def test_duplicate_id_does_not_increase_count(
    store: EpisodicMemory,
) -> None:
    first = MemoryRecord(
        id="episode-1",
        content="first event",
    )
    second = MemoryRecord(
        id="episode-1",
        content="second event",
    )

    store.store(first)
    store.store(second)

    assert store.count() == 1


def test_duplicate_id_preserves_position(
    store: EpisodicMemory,
) -> None:
    first = MemoryRecord(
        id="episode-1",
        content="first",
    )
    second = MemoryRecord(
        id="episode-2",
        content="second",
    )
    replacement = MemoryRecord(
        id="episode-1",
        content="replacement",
    )

    store.store(first)
    store.store(second)
    store.store(replacement)

    assert store.all() == (replacement, second)


def test_store_rejects_non_record(
    store: EpisodicMemory,
) -> None:
    with pytest.raises(TypeError, match="record must be a MemoryRecord"):
        store.store("not-a-record")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "record_id",
    [
        None,
        123,
        object(),
        [],
        {},
    ],
)
def test_get_rejects_non_string_id(
    store: EpisodicMemory,
    record_id: object,
) -> None:
    with pytest.raises(TypeError, match="record_id must be a string"):
        store.get(record_id)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "record_id",
    [
        None,
        123,
        object(),
        [],
        {},
    ],
)
def test_delete_rejects_non_string_id(
    store: EpisodicMemory,
    record_id: object,
) -> None:
    with pytest.raises(TypeError, match="record_id must be a string"):
        store.delete(record_id)  # type: ignore[arg-type]


def test_all_returns_snapshot(
    store: EpisodicMemory,
) -> None:
    first = MemoryRecord(content="event-1")
    second = MemoryRecord(content="event-2")

    store.store(first)
    snapshot = store.all()

    store.store(second)

    assert snapshot == (first,)
    assert store.all() == (first, second)


def test_delete_then_reinsert_moves_record_to_end(
    store: EpisodicMemory,
) -> None:
    first = MemoryRecord(id="episode-1", content="first")
    second = MemoryRecord(id="episode-2", content="second")

    store.store(first)
    store.store(second)

    assert store.delete(first.id) is True
    store.store(first)

    assert store.all() == (second, first)


def test_get_does_not_mutate_store(
    store: EpisodicMemory,
    record: MemoryRecord,
) -> None:
    store.store(record)

    before = store.all()
    result = store.get(record.id)
    after = store.all()

    assert result is record
    assert before == after


def test_delete_does_not_affect_unrelated_records(
    store: EpisodicMemory,
) -> None:
    first = MemoryRecord(id="episode-1", content="first")
    second = MemoryRecord(id="episode-2", content="second")

    store.store(first)
    store.store(second)

    store.delete(first.id)

    assert store.get(second.id) is second
    assert store.all() == (second,)


def test_clear_does_not_replace_store_instance_state(
    store: EpisodicMemory,
    record: MemoryRecord,
) -> None:
    store.store(record)

    store.clear()

    assert store.name == "EpisodicMemory"
    assert store.count() == 0


def test_store_accepts_record_with_metadata(
    store: EpisodicMemory,
) -> None:
    record = MemoryRecord(
        content="experiment event",
        metadata={
            "experiment": "bz-reaction",
            "temperature": 25.0,
        },
    )

    result = store.store(record)

    assert result is record
    assert result.metadata["experiment"] == "bz-reaction"
    assert result.metadata["temperature"] == 25.0


def test_store_preserves_record_fields(
    store: EpisodicMemory,
) -> None:
    created_at = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
    updated_at = datetime(2026, 9, 1, 12, 5, tzinfo=timezone.utc)

    record = MemoryRecord(
        id="episode-42",
        content="system observed an event",
        metadata={"source": "sensor"},
        created_at=created_at,
        updated_at=updated_at,
    )

    result = store.store(record)

    assert result is record
    assert result.id == "episode-42"
    assert result.content == "system observed an event"
    assert result.metadata == {"source": "sensor"}
    assert result.created_at == created_at
    assert result.updated_at == updated_at

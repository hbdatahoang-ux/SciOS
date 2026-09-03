from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

import pytest

from scios.cognitive_core.memory.core import (
    MemoryKind,
    MemoryRecord,
    MemoryStore,
)
from scios.cognitive_core.memory.manager import MemoryManager
from scios.cognitive_core.memory.retrieval import (
    KeywordRetrieval,
    RetrievalStrategy,
)
from scios.cognitive_core.memory.stores import (
    EpisodicMemory,
    SemanticMemory,
    WorkingMemory,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def stores() -> tuple[MemoryStore, MemoryStore, MemoryStore]:
    return (
        WorkingMemory(capacity=10),
        EpisodicMemory(),
        SemanticMemory(),
    )


@pytest.fixture
def manager(
    stores: tuple[MemoryStore, MemoryStore, MemoryStore],
) -> MemoryManager:
    working, episodic, semantic = stores

    return MemoryManager(
        working=working,
        episodic=episodic,
        semantic=semantic,
    )


def make_record(
    content: str,
    *,
    record_id: str = "id-1",
) -> MemoryRecord:
    return MemoryRecord(
        id=record_id,
        content=content,
        created_at=datetime.now(timezone.utc),
    )


class RecordingStrategy(RetrievalStrategy):
    """Test double used to verify retrieval delegation."""

    def __init__(self) -> None:
        super().__init__(name="Recording")
        self.calls: list[
            tuple[tuple[MemoryRecord, ...], object]
        ] = []

    def retrieve(
        self,
        records: Iterable[MemoryRecord],
        query: object,
    ) -> tuple[MemoryRecord, ...]:
        snapshot = tuple(records)
        self.calls.append((snapshot, query))
        return snapshot


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_manager_constructs_with_three_stores(
    stores: tuple[MemoryStore, MemoryStore, MemoryStore],
) -> None:
    working, episodic, semantic = stores

    manager = MemoryManager(
        working=working,
        episodic=episodic,
        semantic=semantic,
    )

    assert manager.working is working
    assert manager.episodic is episodic
    assert manager.semantic is semantic


@pytest.mark.parametrize(
    "field",
    ["working", "episodic", "semantic"],
)
def test_manager_rejects_invalid_store(
    field: str,
    stores: tuple[MemoryStore, MemoryStore, MemoryStore],
) -> None:
    working, episodic, semantic = stores

    values: dict[str, object] = {
        "working": working,
        "episodic": episodic,
        "semantic": semantic,
    }

    values[field] = object()

    with pytest.raises(TypeError):
        MemoryManager(**values)  # type: ignore[arg-type]


def test_manager_requires_keyword_arguments() -> None:
    working = WorkingMemory()
    episodic = EpisodicMemory()
    semantic = SemanticMemory()

    with pytest.raises(TypeError):
        MemoryManager(working, episodic, semantic)  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Store routing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("kind", "attribute"),
    [
        (MemoryKind.WORKING, "working"),
        (MemoryKind.EPISODIC, "episodic"),
        (MemoryKind.SEMANTIC, "semantic"),
    ],
)
def test_store_routes_to_correct_store(
    manager: MemoryManager,
    kind: MemoryKind,
    attribute: str,
) -> None:
    target = getattr(manager, attribute)
    item = make_record(
        f"{kind.value} content",
        record_id=kind.value,
    )

    result = manager.store(item, kind)

    assert result is item
    assert target.get(item.id) is item
    assert target.count() == 1

    for other in (
        manager.working,
        manager.episodic,
        manager.semantic,
    ):
        if other is not target:
            assert other.count() == 0


def test_store_rejects_invalid_record(
    manager: MemoryManager,
) -> None:
    with pytest.raises(TypeError):
        manager.store(object(), MemoryKind.WORKING)  # type: ignore[arg-type]


def test_store_rejects_invalid_kind(
    manager: MemoryManager,
) -> None:
    item = make_record("content")

    with pytest.raises(TypeError):
        manager.store(item, "working")  # type: ignore[arg-type]


@pytest.mark.parametrize("invalid_kind", [None, "working", 1, object()])
def test_store_rejects_non_memory_kind(
    manager: MemoryManager,
    invalid_kind: object,
) -> None:
    item = make_record("content")

    with pytest.raises(TypeError):
        manager.store(item, invalid_kind)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------


def test_get_routes_to_correct_store(
    manager: MemoryManager,
) -> None:
    item = make_record("hello", record_id="x")

    manager.store(item, MemoryKind.EPISODIC)

    assert manager.get("x", MemoryKind.EPISODIC) is item
    assert manager.get("x", MemoryKind.WORKING) is None
    assert manager.get("x", MemoryKind.SEMANTIC) is None


def test_get_missing_returns_none(
    manager: MemoryManager,
) -> None:
    assert manager.get("missing", MemoryKind.WORKING) is None


def test_get_rejects_invalid_record_id(
    manager: MemoryManager,
) -> None:
    with pytest.raises(TypeError):
        manager.get(123, MemoryKind.WORKING)  # type: ignore[arg-type]


def test_get_rejects_invalid_kind(
    manager: MemoryManager,
) -> None:
    with pytest.raises(TypeError):
        manager.get("id", "working")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


def test_delete_routes_to_correct_store(
    manager: MemoryManager,
) -> None:
    item = make_record("hello", record_id="x")

    manager.store(item, MemoryKind.SEMANTIC)

    assert manager.delete("x", MemoryKind.SEMANTIC) is True
    assert manager.get("x", MemoryKind.SEMANTIC) is None

    assert manager.count(MemoryKind.WORKING) == 0
    assert manager.count(MemoryKind.EPISODIC) == 0


def test_delete_missing_returns_false(
    manager: MemoryManager,
) -> None:
    assert manager.delete("missing", MemoryKind.WORKING) is False


def test_delete_rejects_invalid_record_id(
    manager: MemoryManager,
) -> None:
    with pytest.raises(TypeError):
        manager.delete(123, MemoryKind.WORKING)  # type: ignore[arg-type]


def test_delete_rejects_invalid_kind(
    manager: MemoryManager,
) -> None:
    with pytest.raises(TypeError):
        manager.delete("id", "working")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Clear
# ---------------------------------------------------------------------------


def test_clear_affects_only_selected_store(
    manager: MemoryManager,
) -> None:
    working_item = make_record("working", record_id="w")
    episodic_item = make_record("episodic", record_id="e")

    manager.store(working_item, MemoryKind.WORKING)
    manager.store(episodic_item, MemoryKind.EPISODIC)

    manager.clear(MemoryKind.WORKING)

    assert manager.count(MemoryKind.WORKING) == 0
    assert manager.count(MemoryKind.EPISODIC) == 1
    assert manager.get("e", MemoryKind.EPISODIC) is episodic_item


def test_clear_does_not_affect_other_stores(
    manager: MemoryManager,
) -> None:
    working = make_record("working", record_id="w")
    episodic = make_record("episodic", record_id="e")
    semantic = make_record("semantic", record_id="s")

    manager.store(working, MemoryKind.WORKING)
    manager.store(episodic, MemoryKind.EPISODIC)
    manager.store(semantic, MemoryKind.SEMANTIC)

    manager.clear(MemoryKind.EPISODIC)

    assert manager.all(MemoryKind.WORKING) == (working,)
    assert manager.all(MemoryKind.EPISODIC) == ()
    assert manager.all(MemoryKind.SEMANTIC) == (semantic,)


def test_clear_rejects_invalid_kind(
    manager: MemoryManager,
) -> None:
    with pytest.raises(TypeError):
        manager.clear("working")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Count
# ---------------------------------------------------------------------------


def test_count_routes_to_correct_store(
    manager: MemoryManager,
) -> None:
    manager.store(
        make_record("one", record_id="1"),
        MemoryKind.WORKING,
    )
    manager.store(
        make_record("two", record_id="2"),
        MemoryKind.WORKING,
    )
    manager.store(
        make_record("three", record_id="3"),
        MemoryKind.SEMANTIC,
    )

    assert manager.count(MemoryKind.WORKING) == 2
    assert manager.count(MemoryKind.EPISODIC) == 0
    assert manager.count(MemoryKind.SEMANTIC) == 1


def test_count_rejects_invalid_kind(
    manager: MemoryManager,
) -> None:
    with pytest.raises(TypeError):
        manager.count("semantic")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# All
# ---------------------------------------------------------------------------


def test_all_returns_records_from_selected_store(
    manager: MemoryManager,
) -> None:
    first = make_record("first", record_id="1")
    second = make_record("second", record_id="2")

    manager.store(first, MemoryKind.EPISODIC)
    manager.store(second, MemoryKind.EPISODIC)

    result = manager.all(MemoryKind.EPISODIC)

    assert isinstance(result, tuple)
    assert result == (first, second)
    assert result[0] is first
    assert result[1] is second


def test_all_isolated_by_kind(
    manager: MemoryManager,
) -> None:
    working = make_record("working", record_id="w")
    semantic = make_record("semantic", record_id="s")

    manager.store(working, MemoryKind.WORKING)
    manager.store(semantic, MemoryKind.SEMANTIC)

    assert manager.all(MemoryKind.WORKING) == (working,)
    assert manager.all(MemoryKind.EPISODIC) == ()
    assert manager.all(MemoryKind.SEMANTIC) == (semantic,)


def test_all_rejects_invalid_kind(
    manager: MemoryManager,
) -> None:
    with pytest.raises(TypeError):
        manager.all("working")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Retrieval delegation
# ---------------------------------------------------------------------------


def test_retrieve_delegates_to_strategy(
    manager: MemoryManager,
) -> None:
    first = make_record("Python memory", record_id="1")
    second = make_record("Other content", record_id="2")

    manager.store(first, MemoryKind.SEMANTIC)
    manager.store(second, MemoryKind.SEMANTIC)

    strategy = KeywordRetrieval()

    result = manager.retrieve(
        strategy,
        "python",
        MemoryKind.SEMANTIC,
    )

    assert result == (first,)
    assert result[0] is first


def test_retrieve_preserves_strategy_identity(
    manager: MemoryManager,
) -> None:
    item = make_record("hello", record_id="1")
    manager.store(item, MemoryKind.WORKING)

    strategy = RecordingStrategy()

    result = manager.retrieve(
        strategy,
        "query",
        MemoryKind.WORKING,
    )

    assert result == (item,)

    assert len(strategy.calls) == 1

    records, query = strategy.calls[0]

    assert records == (item,)
    assert records[0] is item
    assert query == "query"


def test_retrieve_passes_store_snapshot_to_strategy(
    manager: MemoryManager,
) -> None:
    item = make_record("hello", record_id="1")
    manager.store(item, MemoryKind.EPISODIC)

    strategy = RecordingStrategy()

    manager.retrieve(
        strategy,
        "query",
        MemoryKind.EPISODIC,
    )

    assert len(strategy.calls) == 1

    records, query = strategy.calls[0]

    assert isinstance(records, tuple)
    assert records == (item,)
    assert records[0] is item
    assert query == "query"


def test_retrieve_routes_correct_store(
    manager: MemoryManager,
) -> None:
    working = make_record("working match", record_id="w")
    semantic = make_record("semantic match", record_id="s")

    manager.store(working, MemoryKind.WORKING)
    manager.store(semantic, MemoryKind.SEMANTIC)

    strategy = RecordingStrategy()

    result = manager.retrieve(
        strategy,
        "query",
        MemoryKind.SEMANTIC,
    )

    assert result == (semantic,)
    assert len(strategy.calls) == 1

    records, _ = strategy.calls[0]

    assert records == (semantic,)
    assert records[0] is semantic


def test_retrieve_does_not_mutate_store(
    manager: MemoryManager,
) -> None:
    first = make_record("one", record_id="1")
    second = make_record("two", record_id="2")

    manager.store(first, MemoryKind.WORKING)
    manager.store(second, MemoryKind.WORKING)

    strategy = KeywordRetrieval()

    manager.retrieve(
        strategy,
        "one",
        MemoryKind.WORKING,
    )

    assert manager.all(MemoryKind.WORKING) == (first, second)


def test_retrieve_returns_strategy_result_unchanged(
    manager: MemoryManager,
) -> None:
    item = make_record("hello", record_id="1")
    manager.store(item, MemoryKind.WORKING)

    class FixedResultStrategy(RetrievalStrategy):
        def __init__(self) -> None:
            super().__init__(name="FixedResult")

        def retrieve(
            self,
            records: Iterable[MemoryRecord],
            query: object,
        ) -> tuple[MemoryRecord, ...]:
            return (item,)

    strategy = FixedResultStrategy()

    result = manager.retrieve(
        strategy,
        "anything",
        MemoryKind.WORKING,
    )

    assert result == (item,)
    assert result[0] is item


def test_retrieve_rejects_invalid_strategy(
    manager: MemoryManager,
) -> None:
    with pytest.raises(TypeError):
        manager.retrieve(
            object(),
            "query",
            MemoryKind.WORKING,
        )  # type: ignore[arg-type]


def test_retrieve_rejects_invalid_kind(
    manager: MemoryManager,
) -> None:
    strategy = KeywordRetrieval()

    with pytest.raises(TypeError):
        manager.retrieve(
            strategy,
            "query",
            "working",
        )  # type: ignore[arg-type]


def test_retrieve_accepts_strategy_specific_query(
    manager: MemoryManager,
) -> None:
    item = make_record("Python memory", record_id="1")

    manager.store(item, MemoryKind.SEMANTIC)

    strategy = KeywordRetrieval()

    result = manager.retrieve(
        strategy,
        "PYTHON",
        MemoryKind.SEMANTIC,
    )

    assert result == (item,)


# ---------------------------------------------------------------------------
# Record identity / isolation
# ---------------------------------------------------------------------------


def test_manager_does_not_copy_records(
    manager: MemoryManager,
) -> None:
    item = make_record("content", record_id="1")

    stored = manager.store(
        item,
        MemoryKind.WORKING,
    )

    assert stored is item
    assert manager.get(
        "1",
        MemoryKind.WORKING,
    ) is item


def test_manager_allows_same_record_id_in_different_stores(
    manager: MemoryManager,
) -> None:
    working = make_record("working", record_id="same")
    semantic = make_record("semantic", record_id="same")

    manager.store(
        working,
        MemoryKind.WORKING,
    )
    manager.store(
        semantic,
        MemoryKind.SEMANTIC,
    )

    assert manager.get(
        "same",
        MemoryKind.WORKING,
    ) is working

    assert manager.get(
        "same",
        MemoryKind.SEMANTIC,
    ) is semantic


# ---------------------------------------------------------------------------
# Architecture boundaries
# ---------------------------------------------------------------------------


def test_manager_has_no_internal_record_collection(
    manager: MemoryManager,
) -> None:
    assert not hasattr(manager, "_records")


def test_manager_has_no_internal_retrieval_state(
    manager: MemoryManager,
) -> None:
    assert not hasattr(manager, "_retrieval")


def test_empty_manager_has_zero_counts(
    manager: MemoryManager,
) -> None:
    assert manager.count(MemoryKind.WORKING) == 0
    assert manager.count(MemoryKind.EPISODIC) == 0
    assert manager.count(MemoryKind.SEMANTIC) == 0
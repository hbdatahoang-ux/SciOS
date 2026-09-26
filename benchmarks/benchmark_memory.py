from __future__ import annotations

from scios.cognitive_core.memory import (
    EpisodicMemory,
    KeywordRetrieval,
    MemoryKind,
    MemoryManager,
    MemoryRecord,
    SemanticMemory,
    WorkingMemory,
)


def _manager() -> MemoryManager:
    return MemoryManager(
        working=WorkingMemory(),
        episodic=EpisodicMemory(),
        semantic=SemanticMemory(),
    )


def _record(content: str = "benchmark memory record") -> MemoryRecord:
    return MemoryRecord(content=content)


def test_benchmark_working_store(benchmark) -> None:
    store = WorkingMemory()
    record = _record()

    benchmark(store.store, record)


def test_benchmark_working_get(benchmark) -> None:
    store = WorkingMemory()
    record = _record()
    stored = store.store(record)

    benchmark(store.get, stored.id)


def test_benchmark_working_delete(benchmark) -> None:
    store = WorkingMemory()

    def operation() -> None:
        record = store.store(_record())
        store.delete(record.id)

    benchmark(operation)


def test_benchmark_manager_store(benchmark) -> None:
    manager = _manager()
    record = _record()

    benchmark(
        manager.store,
        record,
        MemoryKind.WORKING,
    )


def test_benchmark_manager_get(benchmark) -> None:
    manager = _manager()
    record = manager.store(
        _record(),
        MemoryKind.SEMANTIC,
    )

    benchmark(
        manager.get,
        record.id,
        MemoryKind.SEMANTIC,
    )


def test_benchmark_manager_retrieve(benchmark) -> None:
    manager = _manager()

    for index in range(10):
        manager.store(
            _record(f"benchmark memory record {index}"),
            MemoryKind.SEMANTIC,
        )

    strategy = KeywordRetrieval()
    query = "benchmark"

    benchmark(
        manager.retrieve,
        strategy,
        query,
        MemoryKind.SEMANTIC,
    )


def test_benchmark_keyword_retrieval(benchmark) -> None:
    records = tuple(
        _record(f"benchmark memory record {index}")
        for index in range(20)
    )
    strategy = KeywordRetrieval()

    benchmark(
        strategy.retrieve,
        records,
        "benchmark",
    )

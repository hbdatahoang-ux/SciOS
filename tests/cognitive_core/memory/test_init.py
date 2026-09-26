from __future__ import annotations

import scios.cognitive_core.memory as memory

from scios.cognitive_core.memory.core import (
    MemoryContent,
    MemoryId,
    MemoryKind,
    MemoryMetadata,
    MemoryQuery,
    MemoryRecord,
    MemoryStore,
    MemoryTimestamp,
)
from scios.cognitive_core.memory.manager import MemoryManager
from scios.cognitive_core.memory.retrieval import (
    KeywordRetrieval,
    RetrievalStrategy,
    SemanticRetrieval,
    TemporalRetrieval,
)
from scios.cognitive_core.memory.serialization import MemorySerializer
from scios.cognitive_core.memory.stores import (
    EpisodicMemory,
    SemanticMemory,
    WorkingMemory,
)


EXPECTED_PUBLIC_API = [
    "MemoryStore",
    "MemoryRecord",
    "MemoryId",
    "MemoryContent",
    "MemoryMetadata",
    "MemoryTimestamp",
    "MemoryQuery",
    "MemoryKind",
    "WorkingMemory",
    "EpisodicMemory",
    "SemanticMemory",
    "RetrievalStrategy",
    "KeywordRetrieval",
    "TemporalRetrieval",
    "SemanticRetrieval",
    "MemoryManager",
    "MemorySerializer",
]


def test_root_all_is_exact() -> None:
    assert memory.__all__ == EXPECTED_PUBLIC_API


def test_root_all_has_expected_count() -> None:
    assert len(memory.__all__) == 17


def test_root_all_has_no_duplicates() -> None:
    assert len(memory.__all__) == len(set(memory.__all__))


def test_root_exports_are_available() -> None:
    for name in memory.__all__:
        assert hasattr(memory, name)


def test_root_exports_match_expected_objects() -> None:
    expected = {
        "MemoryStore": MemoryStore,
        "MemoryRecord": MemoryRecord,
        "MemoryId": MemoryId,
        "MemoryContent": MemoryContent,
        "MemoryMetadata": MemoryMetadata,
        "MemoryTimestamp": MemoryTimestamp,
        "MemoryQuery": MemoryQuery,
        "MemoryKind": MemoryKind,
        "WorkingMemory": WorkingMemory,
        "EpisodicMemory": EpisodicMemory,
        "SemanticMemory": SemanticMemory,
        "RetrievalStrategy": RetrievalStrategy,
        "KeywordRetrieval": KeywordRetrieval,
        "TemporalRetrieval": TemporalRetrieval,
        "SemanticRetrieval": SemanticRetrieval,
        "MemoryManager": MemoryManager,
        "MemorySerializer": MemorySerializer,
    }

    for name, expected_object in expected.items():
        assert getattr(memory, name) is expected_object


def test_root_star_import_contract() -> None:
    namespace: dict[str, object] = {}

    exec(
        "from scios.cognitive_core.memory import *",
        namespace,
    )

    for name in EXPECTED_PUBLIC_API:
        assert name in namespace
        assert namespace[name] is getattr(memory, name)


def test_root_core_exports() -> None:
    assert memory.MemoryStore is MemoryStore
    assert memory.MemoryRecord is MemoryRecord
    assert memory.MemoryId is MemoryId
    assert memory.MemoryContent is MemoryContent
    assert memory.MemoryMetadata is MemoryMetadata
    assert memory.MemoryTimestamp is MemoryTimestamp
    assert memory.MemoryQuery is MemoryQuery
    assert memory.MemoryKind is MemoryKind


def test_root_store_exports() -> None:
    assert memory.WorkingMemory is WorkingMemory
    assert memory.EpisodicMemory is EpisodicMemory
    assert memory.SemanticMemory is SemanticMemory


def test_root_retrieval_exports() -> None:
    assert memory.RetrievalStrategy is RetrievalStrategy
    assert memory.KeywordRetrieval is KeywordRetrieval
    assert memory.TemporalRetrieval is TemporalRetrieval
    assert memory.SemanticRetrieval is SemanticRetrieval


def test_root_manager_export() -> None:
    assert memory.MemoryManager is MemoryManager


def test_root_serialization_export() -> None:
    assert memory.MemorySerializer is MemorySerializer

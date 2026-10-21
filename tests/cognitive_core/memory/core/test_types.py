from datetime import datetime

from scios.cognitive_core.memory.core.types import (
    MemoryContent,
    MemoryId,
    MemoryKind,
    MemoryMetadata,
    MemoryQuery,
    MemoryTimestamp,
)


def test_memory_kind_values() -> None:
    assert MemoryKind.WORKING.value == "working"
    assert MemoryKind.EPISODIC.value == "episodic"
    assert MemoryKind.SEMANTIC.value == "semantic"


def test_memory_kind_members() -> None:
    assert set(MemoryKind) == {
        MemoryKind.WORKING,
        MemoryKind.EPISODIC,
        MemoryKind.SEMANTIC,
    }


def test_memory_kind_is_string_enum() -> None:
    assert isinstance(MemoryKind.WORKING, str)
    assert isinstance(MemoryKind.EPISODIC, str)
    assert isinstance(MemoryKind.SEMANTIC, str)


def test_memory_type_aliases_exist() -> None:
    assert MemoryId is not None
    assert MemoryContent is not None
    assert MemoryMetadata is not None
    assert MemoryQuery is not None
    assert MemoryTimestamp is not None


def test_memory_timestamp_alias_targets_datetime() -> None:
    assert MemoryTimestamp == datetime
from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone
from uuid import UUID

import pytest

from scios.cognitive_core.memory.core.errors import MemoryValidationError
from scios.cognitive_core.memory.core.record import MemoryRecord
from scios.cognitive_core.memory.core.types import MemoryKind


def test_record_defaults() -> None:
    record = MemoryRecord(content="hello")

    assert record.content == "hello"
    assert isinstance(record.id, str)
    assert isinstance(UUID(record.id), UUID)
    assert record.metadata == {}
    assert isinstance(record.created_at, datetime)
    assert record.created_at.tzinfo is not None
    assert record.updated_at == record.created_at
    assert record.kind is None


def test_record_accepts_explicit_values() -> None:
    created_at = datetime(2026, 9, 2, 10, 0, tzinfo=timezone.utc)
    updated_at = datetime(2026, 9, 2, 11, 0, tzinfo=timezone.utc)
    metadata = {"source": "test"}
    record = MemoryRecord(
        content="hello",
        id="memory-1",
        metadata=metadata,
        created_at=created_at,
        updated_at=updated_at,
        kind=MemoryKind.EPISODIC,
    )

    assert record.content == "hello"
    assert record.id == "memory-1"
    assert record.metadata == metadata
    assert record.created_at == created_at
    assert record.updated_at == updated_at
    assert record.kind is MemoryKind.EPISODIC


@pytest.mark.parametrize("content", ["", " ", "\t", "\n"])
def test_content_must_be_non_empty_string(content: str) -> None:
    with pytest.raises(
        MemoryValidationError,
        match="content must be a non-empty string",
    ):
        MemoryRecord(content=content)


@pytest.mark.parametrize("content", [None, 123, [], {}, object()])
def test_content_must_be_string(content: object) -> None:
    with pytest.raises(
        MemoryValidationError,
        match="content must be a non-empty string",
    ):
        MemoryRecord(content=content)  # type: ignore[arg-type]


@pytest.mark.parametrize("record_id", ["", " ", "\t", "\n", None, 123])
def test_id_must_be_non_empty_string(record_id: object) -> None:
    with pytest.raises(
        MemoryValidationError,
        match="id must be a non-empty string",
    ):
        MemoryRecord(
            content="hello",
            id=record_id,  # type: ignore[arg-type]
        )


def test_generated_ids_are_unique() -> None:
    first = MemoryRecord(content="first")
    second = MemoryRecord(content="second")

    assert first.id != second.id


@pytest.mark.parametrize("metadata", [None, [], (), "metadata", 123])
def test_metadata_must_be_dictionary(metadata: object) -> None:
    with pytest.raises(
        MemoryValidationError,
        match="metadata must be a dictionary",
    ):
        MemoryRecord(
            content="hello",
            metadata=metadata,  # type: ignore[arg-type]
        )


def test_metadata_is_defensively_copied() -> None:
    metadata = {"source": "test"}
    record = MemoryRecord(content="hello", metadata=metadata)

    metadata["source"] = "changed"
    metadata["new"] = "value"

    assert record.metadata == {"source": "test"}


def test_created_at_must_be_datetime() -> None:
    with pytest.raises(
        MemoryValidationError,
        match="created_at must be a datetime",
    ):
        MemoryRecord(
            content="hello",
            created_at="2026-09-02",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("updated_at", [None, "2026-09-02", 123, object()])
def test_updated_at_contract(updated_at: object) -> None:
    if updated_at is None:
        record = MemoryRecord(content="hello")
        assert record.updated_at == record.created_at
    else:
        with pytest.raises(
            MemoryValidationError,
            match="updated_at must be a datetime or None",
        ):
            MemoryRecord(
                content="hello",
                updated_at=updated_at,  # type: ignore[arg-type]
            )


def test_kind_accepts_memory_kind() -> None:
    record = MemoryRecord(
        content="hello",
        kind=MemoryKind.SEMANTIC,
    )

    assert record.kind is MemoryKind.SEMANTIC


def test_kind_accepts_none() -> None:
    record = MemoryRecord(content="hello", kind=None)

    assert record.kind is None


@pytest.mark.parametrize("kind", ["semantic", "working", 1, object()])
def test_kind_must_be_memory_kind_or_none(kind: object) -> None:
    with pytest.raises(
        MemoryValidationError,
        match="kind must be a MemoryKind or None",
    ):
        MemoryRecord(
            content="hello",
            kind=kind,  # type: ignore[arg-type]
        )


def test_record_is_frozen() -> None:
    record = MemoryRecord(content="hello")

    with pytest.raises(FrozenInstanceError):
        record.content = "changed"  # type: ignore[misc]


def test_record_uses_slots() -> None:
    record = MemoryRecord(content="hello")

    assert not hasattr(record, "__dict__")


def test_record_is_dataclass() -> None:
    record_fields = fields(MemoryRecord)

    assert [field.name for field in record_fields] == [
        "content",
        "id",
        "metadata",
        "created_at",
        "updated_at",
        "kind",
    ]


def test_record_metadata_isolated_between_records() -> None:
    first = MemoryRecord(content="first", metadata={"value": 1})
    second = MemoryRecord(content="second", metadata={"value": 2})

    assert first.metadata is not second.metadata
    assert first.metadata == {"value": 1}
    assert second.metadata == {"value": 2}
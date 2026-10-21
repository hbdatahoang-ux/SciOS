from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from scios.cognitive_core.memory.core import (
    MemoryKind,
    MemoryRecord,
    MemorySerializationError,
)
from scios.cognitive_core.memory.serialization import MemorySerializer


@pytest.fixture
def serializer() -> MemorySerializer:
    return MemorySerializer()


@pytest.fixture
def record() -> MemoryRecord:
    return MemoryRecord(
        id="memory-001",
        content="SciOS memory contract",
        metadata={
            "source": "test",
            "score": 0.95,
            "tags": ["scios", "memory"],
        },
        created_at=datetime(
            2026,
            9,
            2,
            10,
            30,
            15,
            123456,
            tzinfo=timezone.utc,
        ),
        updated_at=datetime(
            2026,
            9,
            2,
            11,
            45,
            20,
            654321,
            tzinfo=timezone.utc,
        ),
        kind=MemoryKind.SEMANTIC,
    )


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_serializer_can_be_instantiated() -> None:
    serializer = MemorySerializer()

    assert isinstance(serializer, MemorySerializer)


def test_serializer_is_stateless(serializer: MemorySerializer) -> None:
    assert not hasattr(serializer, "_records")
    assert not hasattr(serializer, "records")


def test_serializer_has_no_store_dependency(serializer: MemorySerializer) -> None:
    assert not hasattr(serializer, "store")
    assert not hasattr(serializer, "working")
    assert not hasattr(serializer, "episodic")
    assert not hasattr(serializer, "semantic")


# ---------------------------------------------------------------------------
# serialize()
# ---------------------------------------------------------------------------


def test_serialize_returns_dict(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.serialize(record)

    assert isinstance(result, dict)


def test_serialize_contains_expected_fields(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.serialize(record)

    assert set(result) == {
        "id",
        "content",
        "metadata",
        "created_at",
        "updated_at",
        "kind",
    }


def test_serialize_preserves_id(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.serialize(record)

    assert result["id"] == record.id


def test_serialize_preserves_content(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.serialize(record)

    assert result["content"] == record.content


def test_serialize_copies_metadata(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.serialize(record)

    assert result["metadata"] == record.metadata
    assert result["metadata"] is not record.metadata


def test_serialize_preserves_created_at_as_iso_string(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.serialize(record)

    assert result["created_at"] == record.created_at.isoformat()
    assert isinstance(result["created_at"], str)


def test_serialize_preserves_updated_at_as_iso_string(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.serialize(record)

    assert result["updated_at"] == record.updated_at.isoformat()
    assert isinstance(result["updated_at"], str)


def test_serialize_preserves_kind_value(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.serialize(record)

    assert result["kind"] == MemoryKind.SEMANTIC.value


@pytest.mark.parametrize(
    "kind",
    [
        MemoryKind.WORKING,
        MemoryKind.EPISODIC,
        MemoryKind.SEMANTIC,
    ],
)
def test_serialize_supports_all_memory_kinds(
    serializer: MemorySerializer,
    kind: MemoryKind,
) -> None:
    record = MemoryRecord(
        id=f"{kind.value}-001",
        content="memory",
        kind=kind,
    )

    result = serializer.serialize(record)

    assert result["kind"] == kind.value


def test_serialize_supports_none_updated_at(
    serializer: MemorySerializer,
) -> None:
    created_at = datetime.now(timezone.utc)

    record = MemoryRecord(
        id="memory-002",
        content="memory",
        created_at=created_at,
        updated_at=None,
    )

    result = serializer.serialize(record)

    assert result["updated_at"] == created_at.isoformat()


def test_serialize_supports_none_kind(
    serializer: MemorySerializer,
) -> None:
    record = MemoryRecord(
        id="memory-003",
        content="memory",
        kind=None,
    )

    result = serializer.serialize(record)

    assert result["kind"] is None


def test_serialize_rejects_non_record(
    serializer: MemorySerializer,
) -> None:
    with pytest.raises(TypeError, match="record must be a MemoryRecord"):
        serializer.serialize("invalid")  # type: ignore[arg-type]


def test_serialize_does_not_mutate_record(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    original_metadata = dict(record.metadata)
    original_created_at = record.created_at
    original_updated_at = record.updated_at
    original_kind = record.kind

    serializer.serialize(record)

    assert record.metadata == original_metadata
    assert record.created_at == original_created_at
    assert record.updated_at == original_updated_at
    assert record.kind == original_kind


# ---------------------------------------------------------------------------
# deserialize()
# ---------------------------------------------------------------------------


def test_deserialize_returns_memory_record(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    data = serializer.serialize(record)

    result = serializer.deserialize(data)

    assert isinstance(result, MemoryRecord)


def test_deserialize_preserves_id(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.deserialize(serializer.serialize(record))

    assert result.id == record.id


def test_deserialize_preserves_content(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.deserialize(serializer.serialize(record))

    assert result.content == record.content


def test_deserialize_preserves_metadata(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.deserialize(serializer.serialize(record))

    assert result.metadata == record.metadata


def test_deserialize_reconstructs_created_at(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.deserialize(serializer.serialize(record))

    assert result.created_at == record.created_at
    assert isinstance(result.created_at, datetime)


def test_deserialize_reconstructs_updated_at(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.deserialize(serializer.serialize(record))

    assert result.updated_at == record.updated_at
    assert isinstance(result.updated_at, datetime)


def test_deserialize_reconstructs_memory_kind(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.deserialize(serializer.serialize(record))

    assert result.kind == record.kind
    assert isinstance(result.kind, MemoryKind)


def test_deserialize_returns_equal_but_distinct_record(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.deserialize(serializer.serialize(record))

    assert result == record
    assert result is not record


def test_deserialize_copies_metadata(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    data = serializer.serialize(record)

    result = serializer.deserialize(data)

    assert result.metadata == record.metadata
    assert result.metadata is not data["metadata"]


def test_deserialize_rejects_non_dict(
    serializer: MemorySerializer,
) -> None:
    with pytest.raises(TypeError, match="data must be a dictionary"):
        serializer.deserialize("invalid")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field",
    [
        "id",
        "content",
        "created_at",
    ],
)
def test_deserialize_missing_required_field_raises(
    serializer: MemorySerializer,
    record: MemoryRecord,
    field: str,
) -> None:
    data = serializer.serialize(record)
    del data[field]

    with pytest.raises(MemorySerializationError):
        serializer.deserialize(data)


def test_deserialize_missing_required_field_reports_field(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    data = serializer.serialize(record)
    del data["content"]

    with pytest.raises(
        MemorySerializationError,
        match="missing required field: content",
    ):
        serializer.deserialize(data)


@pytest.mark.parametrize(
    "created_at",
    [
        "invalid-datetime",
        "",
        "2026",
    ],
)
def test_deserialize_invalid_created_at_raises(
    serializer: MemorySerializer,
    record: MemoryRecord,
    created_at: str,
) -> None:
    data = serializer.serialize(record)
    data["created_at"] = created_at

    with pytest.raises(MemorySerializationError):
        serializer.deserialize(data)


def test_deserialize_invalid_updated_at_raises(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    data = serializer.serialize(record)
    data["updated_at"] = "invalid-datetime"

    with pytest.raises(MemorySerializationError):
        serializer.deserialize(data)


@pytest.mark.parametrize(
    "kind",
    [
        "invalid",
        "",
        123,
        {},
    ],
)
def test_deserialize_invalid_kind_raises(
    serializer: MemorySerializer,
    record: MemoryRecord,
    kind: object,
) -> None:
    data = serializer.serialize(record)
    data["kind"] = kind

    with pytest.raises(MemorySerializationError):
        serializer.deserialize(data)


@pytest.mark.parametrize(
    "metadata",
    [
        None,
        [],
        "metadata",
        123,
    ],
)
def test_deserialize_invalid_metadata_raises(
    serializer: MemorySerializer,
    record: MemoryRecord,
    metadata: object,
) -> None:
    data = serializer.serialize(record)
    data["metadata"] = metadata

    with pytest.raises(MemorySerializationError):
        serializer.deserialize(data)


def test_deserialize_invalid_id_raises(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    data = serializer.serialize(record)
    data["id"] = ""

    with pytest.raises(MemorySerializationError):
        serializer.deserialize(data)


def test_deserialize_invalid_content_raises(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    data = serializer.serialize(record)
    data["content"] = ""

    with pytest.raises(MemorySerializationError):
        serializer.deserialize(data)


# ---------------------------------------------------------------------------
# dumps()
# ---------------------------------------------------------------------------


def test_dumps_returns_string(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.dumps(record)

    assert isinstance(result, str)


def test_dumps_produces_valid_json(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    payload = serializer.dumps(record)

    result = json.loads(payload)

    assert isinstance(result, dict)


def test_dumps_preserves_unicode(
    serializer: MemorySerializer,
) -> None:
    record = MemoryRecord(
        id="unicode-001",
        content="SciOS – hệ thống khoa học",
        metadata={"label": "Việt Nam"},
    )

    payload = serializer.dumps(record)

    assert "SciOS – hệ thống khoa học" in payload
    assert "Việt Nam" in payload


def test_dumps_is_deterministic(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    first = serializer.dumps(record)
    second = serializer.dumps(record)

    assert first == second


def test_dumps_uses_sorted_keys(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    payload = serializer.dumps(record)

    data = json.loads(payload)
    keys = list(data.keys())

    assert keys == sorted(keys)


def test_dumps_rejects_non_record(
    serializer: MemorySerializer,
) -> None:
    with pytest.raises(TypeError, match="record must be a MemoryRecord"):
        serializer.dumps(None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# loads()
# ---------------------------------------------------------------------------


def test_loads_returns_memory_record(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    payload = serializer.dumps(record)

    result = serializer.loads(payload)

    assert isinstance(result, MemoryRecord)


def test_loads_round_trip(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    payload = serializer.dumps(record)

    result = serializer.loads(payload)

    assert result == record


def test_loads_rejects_non_string(
    serializer: MemorySerializer,
) -> None:
    with pytest.raises(TypeError, match="payload must be a string"):
        serializer.loads(None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "payload",
    [
        "",
        "invalid json",
        "{",
        "[]",
        "null",
        "123",
        '"string"',
    ],
)
def test_loads_invalid_payload_raises(
    serializer: MemorySerializer,
    payload: str,
) -> None:
    if payload in {"[]", "null", "123", '"string"'}:
        with pytest.raises(MemorySerializationError):
            serializer.loads(payload)
    else:
        with pytest.raises(MemorySerializationError):
            serializer.loads(payload)


def test_loads_missing_field_raises(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    data = serializer.serialize(record)
    del data["id"]

    payload = json.dumps(data)

    with pytest.raises(MemorySerializationError):
        serializer.loads(payload)


def test_loads_invalid_record_data_raises(
    serializer: MemorySerializer,
) -> None:
    payload = json.dumps(
        {
            "id": "memory-001",
            "content": "",
            "metadata": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": None,
            "kind": None,
        }
    )

    with pytest.raises(MemorySerializationError):
        serializer.loads(payload)


# ---------------------------------------------------------------------------
# Round-trip invariants
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "kind",
    [
        None,
        MemoryKind.WORKING,
        MemoryKind.EPISODIC,
        MemoryKind.SEMANTIC,
    ],
)
def test_round_trip_preserves_kind(
    serializer: MemorySerializer,
    kind: MemoryKind | None,
) -> None:
    record = MemoryRecord(
        id="roundtrip-kind",
        content="memory",
        kind=kind,
    )

    result = serializer.loads(serializer.dumps(record))

    assert result.kind == kind


@pytest.mark.parametrize(
    "metadata",
    [
        {},
        {"source": "test"},
        {"score": 0.95, "count": 3},
        {"nested": {"value": True}},
        {"tags": ["a", "b", "c"]},
        {"unicode": "Việt Nam"},
    ],
)
def test_round_trip_preserves_metadata(
    serializer: MemorySerializer,
    metadata: dict[str, object],
) -> None:
    record = MemoryRecord(
        id="roundtrip-metadata",
        content="memory",
        metadata=metadata,
    )

    result = serializer.loads(serializer.dumps(record))

    assert result.metadata == metadata


def test_round_trip_preserves_timezone(
    serializer: MemorySerializer,
) -> None:
    created_at = datetime(
        2026,
        9,
        2,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    record = MemoryRecord(
        id="timezone-001",
        content="timezone test",
        created_at=created_at,
    )

    result = serializer.loads(serializer.dumps(record))

    assert result.created_at == created_at
    assert result.created_at.tzinfo == timezone.utc


def test_round_trip_preserves_microseconds(
    serializer: MemorySerializer,
) -> None:
    created_at = datetime(
        2026,
        9,
        2,
        12,
        0,
        0,
        987654,
        tzinfo=timezone.utc,
    )

    record = MemoryRecord(
        id="microseconds-001",
        content="precision test",
        created_at=created_at,
    )

    result = serializer.loads(serializer.dumps(record))

    assert result.created_at == created_at


def test_round_trip_does_not_share_metadata_object(
    serializer: MemorySerializer,
    record: MemoryRecord,
) -> None:
    result = serializer.loads(serializer.dumps(record))

    assert result.metadata == record.metadata
    assert result.metadata is not record.metadata
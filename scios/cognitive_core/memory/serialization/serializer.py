from __future__ import annotations

from datetime import datetime
from typing import Any

from scios.cognitive_core.memory.core import (
    MemoryRecord,
    MemorySerializationError,
    MemoryValidationError,
)


class MemorySerializer:
    """Serialize and deserialize MemoryRecord instances."""

    def serialize(self, record: MemoryRecord) -> dict[str, Any]:
        if not isinstance(record, MemoryRecord):
            raise TypeError("record must be a MemoryRecord")

        try:
            return {
                "id": record.id,
                "content": record.content,
                "metadata": dict(record.metadata),
                "created_at": record.created_at.isoformat(),
                "updated_at": (
                    record.updated_at.isoformat()
                    if record.updated_at is not None
                    else None
                ),
                "kind": (
                    record.kind.value
                    if record.kind is not None
                    else None
                ),
            }
        except (AttributeError, TypeError, ValueError) as exc:
            raise MemorySerializationError(
                "failed to serialize memory record"
            ) from exc

    def deserialize(self, data: dict[str, Any]) -> MemoryRecord:
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")

        try:
            record_id = data["id"]
            content = data["content"]
            metadata = data.get("metadata", {})
            created_at = datetime.fromisoformat(data["created_at"])

            updated_at_raw = data.get("updated_at")
            updated_at = (
                datetime.fromisoformat(updated_at_raw)
                if updated_at_raw is not None
                else None
            )

            kind_raw = data.get("kind")

            from scios.cognitive_core.memory.core import MemoryKind

            kind = (
                MemoryKind(kind_raw)
                if kind_raw is not None
                else None
            )

            return MemoryRecord(
                id=record_id,
                content=content,
                metadata=metadata,
                created_at=created_at,
                updated_at=updated_at,
                kind=kind,
            )

        except KeyError as exc:
            raise MemorySerializationError(
                f"missing required field: {exc.args[0]}"
            ) from exc

        except (TypeError, ValueError, MemoryValidationError) as exc:
            raise MemorySerializationError(
                "failed to deserialize memory record"
            ) from exc

    def dumps(self, record: MemoryRecord) -> str:
        import json

        return json.dumps(
            self.serialize(record),
            ensure_ascii=False,
            sort_keys=True,
        )

    def loads(self, payload: str) -> MemoryRecord:
        import json

        if not isinstance(payload, str):
            raise TypeError("payload must be a string")

        try:
            data = json.loads(payload)
        except (json.JSONDecodeError, TypeError) as exc:
            raise MemorySerializationError(
                "invalid JSON payload"
            ) from exc

        try:
            return self.deserialize(data)
        except TypeError as exc:
            raise MemorySerializationError(
                "invalid serialized memory record"
            ) from exc
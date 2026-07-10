import json
from dataclasses import dataclass
from typing import List, Dict, Any
from scios.execution.context.timeline.record import TimelineRecord


@dataclass
class TimelineSerializer:
    """
    TimelineSerializer = Export/Import timeline to JSON or dict.
    """

    # =========================================================
    # Export
    # =========================================================

    def to_dict(self, records: List[TimelineRecord]) -> List[Dict[str, Any]]:
        """
        Convert timeline records to list of dicts.
        """
        return [
            {
                "event": {
                    "event_id": str(r.event.event_id),
                    "event_type": r.event.event_type.value,
                    "node_id": str(r.event.node_id) if r.event.node_id else None,
                    "snapshot_id": str(r.event.snapshot_id) if r.event.snapshot_id else None,
                    "timestamp": r.event.timestamp.isoformat(),
                    "metadata": r.event.metadata,
                },
                "snapshot": r.snapshot.to_dict(),
            }
            for r in records
        ]

    def to_json(self, records: List[TimelineRecord]) -> str:
        """
        Convert timeline records to JSON string.
        """
        return json.dumps(self.to_dict(records), indent=2)

    # =========================================================
    # Import
    # =========================================================

    def from_dict(self, data: List[Dict[str, Any]]) -> List[TimelineRecord]:
        """
        Reconstruct timeline records from dicts.
        """
        # ⚠️ Simplified: assumes ExecutionSnapshot.from_dict exists
        from scios.execution.context.snapshot.snapshot import ExecutionSnapshot
        from scios.execution.context.timeline.event import TimelineEvent, TimelineEventType
        from uuid import UUID
        from datetime import datetime

        records = []
        for item in data:
            event_data = item["event"]
            snapshot_data = item["snapshot"]

            event = TimelineEvent(
                event_id=UUID(event_data["event_id"]),
                event_type=TimelineEventType(event_data["event_type"]),
                node_id=UUID(event_data["node_id"]) if event_data["node_id"] else None,
                snapshot_id=UUID(event_data["snapshot_id"]) if event_data["snapshot_id"] else None,
                timestamp=datetime.fromisoformat(event_data["timestamp"]),
                metadata=event_data["metadata"],
            )

            snapshot = ExecutionSnapshot(**snapshot_data)
            records.append(TimelineRecord(event=event, snapshot=snapshot))
        return records

    def from_json(self, data: str) -> List[TimelineRecord]:
        """
        Reconstruct timeline records from JSON string.
        """
        return self.from_dict(json.loads(data))

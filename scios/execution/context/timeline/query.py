from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from scios.execution.context.timeline.record import TimelineRecord
from scios.execution.node.status import NodeStatus


@dataclass
class TimelineQueryEngine:
    """
    TimelineQueryEngine = Query API for execution timeline.
    Supports filtering by node, status, time, and metadata.
    """

    records: List[TimelineRecord]

    # =========================================================
    # Node-based queries
    # =========================================================

    def by_node(self, node_id: UUID) -> List[TimelineRecord]:
        """
        Get all records for a given node.
        """
        return [r for r in self.records if r.event.node_id == node_id]

    def by_status(self, status: NodeStatus) -> List[TimelineRecord]:
        """
        Get all records where snapshot context has node in given status.
        """
        return [r for r in self.records if getattr(r.snapshot.context, "status", None) == status]

    # =========================================================
    # Time-based queries
    # =========================================================

    def between(self, start: datetime, end: datetime) -> List[TimelineRecord]:
        """
        Get all records between two timestamps.
        """
        return [r for r in self.records if start <= r.event.timestamp <= end]

    def after(self, ts: datetime) -> List[TimelineRecord]:
        """
        Get all records after a timestamp.
        """
        return [r for r in self.records if r.event.timestamp > ts]

    def before(self, ts: datetime) -> List[TimelineRecord]:
        """
        Get all records before a timestamp.
        """
        return [r for r in self.records if r.event.timestamp < ts]

    # =========================================================
    # Metadata queries
    # =========================================================

    def by_metadata(self, key: str, value: str) -> List[TimelineRecord]:
        """
        Get all records where event metadata matches key/value.
        """
        return [r for r in self.records if r.event.metadata.get(key) == value]

    # =========================================================
    # Utility
    # =========================================================

    def latest(self) -> Optional[TimelineRecord]:
        """
        Get latest record in timeline.
        """
        return self.records[-1] if self.records else None

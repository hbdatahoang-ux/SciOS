from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID
from scios.execution.context.timeline.record import TimelineRecord


@dataclass
class TimelineManager:
    """
    TimelineManager = Manages full execution timeline.
    """

    records: List[TimelineRecord] = field(default_factory=list)

    def add_record(self, record: TimelineRecord) -> None:
        self.records.append(record)

    def latest(self) -> Optional[TimelineRecord]:
        return self.records[-1] if self.records else None

    def filter_by_node(self, node_id: UUID) -> List[TimelineRecord]:
        return [r for r in self.records if r.event.node_id == node_id]

    def filter_by_event(self, event_type: str) -> List[TimelineRecord]:
        return [r for r in self.records if r.event.event_type.value == event_type]

    def history(self) -> List[UUID]:
        return [r.event.event_id for r in self.records]

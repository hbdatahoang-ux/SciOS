from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


class TimelineEventType(Enum):
    NODE_CREATED = "node_created"
    NODE_STARTED = "node_started"
    NODE_FINISHED = "node_finished"
    NODE_FAILED = "node_failed"
    SNAPSHOT_TAKEN = "snapshot_taken"


@dataclass(frozen=True)
class TimelineEvent:
    """
    TimelineEvent = Atomic event in execution timeline.
    """

    event_id: UUID = field(default_factory=uuid4)
    event_type: TimelineEventType = TimelineEventType.NODE_CREATED
    node_id: UUID | None = None
    snapshot_id: UUID | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, str] = field(default_factory=dict)

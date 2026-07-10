from dataclasses import dataclass
from scios.execution.context.snapshot.snapshot import ExecutionSnapshot
from scios.execution.context.timeline.event import TimelineEvent


@dataclass(frozen=True)
class TimelineRecord:
    """
    TimelineRecord = Event + Snapshot at a point in time.
    """

    event: TimelineEvent
    snapshot: ExecutionSnapshot

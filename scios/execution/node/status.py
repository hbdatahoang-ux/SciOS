from enum import Enum


class NodeStatus(Enum):
    """Lifecycle state of an ExecutionNode."""

    CREATED = "created"
    READY = "ready"
    WAITING = "waiting"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

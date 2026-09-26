"""
SciOS Runtime Events
====================

Runtime event definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


# ============================================================
# Base Event
# ============================================================

@dataclass(slots=True)
class RuntimeEvent:
    """
    Base class for all runtime events.
    """

    name: str
    context_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    event_id: str = field(
        default_factory=lambda: uuid.uuid4().hex
    )


# ============================================================
# Task Events
# ============================================================

@dataclass(slots=True)
class TaskCreated(RuntimeEvent):

    def __init__(
        self,
        context_id: str,
        payload: dict[str, Any] | None = None,
    ):
        super().__init__(
            name="task.created",
            context_id=context_id,
            payload=payload or {},
        )


@dataclass(slots=True)
class TaskStarted(RuntimeEvent):

    def __init__(
        self,
        context_id: str,
        payload: dict[str, Any] | None = None,
    ):
        super().__init__(
            name="task.started",
            context_id=context_id,
            payload=payload or {},
        )


@dataclass(slots=True)
class TaskCompleted(RuntimeEvent):

    def __init__(
        self,
        context_id: str,
        payload: dict[str, Any] | None = None,
    ):
        super().__init__(
            name="task.completed",
            context_id=context_id,
            payload=payload or {},
        )


@dataclass(slots=True)
class TaskFailed(RuntimeEvent):

    def __init__(
        self,
        context_id: str,
        payload: dict[str, Any] | None = None,
    ):
        super().__init__(
            name="task.failed",
            context_id=context_id,
            payload=payload or {},
        )


# ============================================================
# Pipeline Events
# ============================================================

@dataclass(slots=True)
class StageStarted(RuntimeEvent):

    def __init__(
        self,
        context_id: str,
        stage: str,
    ):
        super().__init__(
            name="stage.started",
            context_id=context_id,
            payload={"stage": stage},
        )


@dataclass(slots=True)
class StageCompleted(RuntimeEvent):

    def __init__(
        self,
        context_id: str,
        stage: str,
    ):
        super().__init__(
            name="stage.completed",
            context_id=context_id,
            payload={"stage": stage},
        )
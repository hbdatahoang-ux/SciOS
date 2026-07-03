"""
SciOS Execution Context
=======================

Global execution context for the SciOS Kernel.

Responsibilities
----------------
- Maintain runtime context
- Share execution metadata
- Store session information
- Provide global context access
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


__all__ = [
    "ExecutionContext",
    "KernelContext",
]


class ExecutionContext:
    """
    Global kernel execution context.

    The execution context stores transient runtime information
    shared across the Kernel during a session.

    Notes
    -----
    This is NOT the cognitive memory of the agent.
    It only stores execution metadata.
    """

    def __init__(self) -> None:

        self.reset()

    # =====================================================
    # Lifecycle
    # =====================================================

    def reset(self) -> None:
        """
        Reset execution context.
        """

        self._created_at = datetime.now(
            timezone.utc
        ).isoformat()

        self._session_id: str | None = None

        self._task_id: int | None = None

        self._values: dict[str, Any] = {}

    # =====================================================
    # Session
    # =====================================================

    @property
    def session_id(self) -> str | None:

        return self._session_id

    @session_id.setter
    def session_id(
        self,
        value: str | None,
    ) -> None:

        self._session_id = value

    # =====================================================
    # Task
    # =====================================================

    @property
    def task_id(self) -> int | None:

        return self._task_id

    @task_id.setter
    def task_id(
        self,
        value: int | None,
    ) -> None:

        self._task_id = value

    # =====================================================
    # Generic Storage
    # =====================================================

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self._values[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self._values.get(
            key,
            default,
        )

    def update(
        self,
        values: dict[str, Any],
    ) -> None:

        self._values.update(values)

    def remove(
        self,
        key: str,
    ) -> None:

        self._values.pop(
            key,
            None,
        )

    def clear(self) -> None:

        self._values.clear()

    # =====================================================
    # Queries
    # =====================================================

    def contains(
        self,
        key: str,
    ) -> bool:

        return key in self._values

    def keys(self):

        return self._values.keys()

    def values(self):

        return self._values.values()

    def items(self):

        return self._values.items()

    def to_dict(self) -> dict[str, Any]:

        return dict(self._values)

    # =====================================================
    # Status
    # =====================================================

    def status(self) -> dict[str, Any]:

        return {

            "created_at": self._created_at,

            "session_id": self._session_id,

            "task_id": self._task_id,

            "entries": len(self._values),
        }

    # =====================================================
    # Python Protocols
    # =====================================================

    def __getitem__(
        self,
        key: str,
    ) -> Any:

        return self._values[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:

        self._values[key] = value

    def __contains__(
        self,
        key: str,
    ) -> bool:

        return key in self._values

    def __len__(self) -> int:

        return len(self._values)

    def __repr__(self) -> str:

        return (
            "ExecutionContext("
            f"session={self._session_id}, "
            f"task={self._task_id}, "
            f"entries={len(self._values)})"
        )
# =====================================================
# Backward Compatibility
# =====================================================

class KernelContext(ExecutionContext):
    """
    Backward-compatible alias.

    Existing kernel modules may still import
    KernelContext while the canonical implementation
    is ExecutionContext.
    """

    pass        
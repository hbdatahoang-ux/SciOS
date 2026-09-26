"""
SciOS Runtime Context
=====================

Runtime execution context for the SciOS Cognitive Kernel.

Responsibilities
----------------
- Manage execution/session context.
- Store runtime variables and metadata.
- Maintain runtime configuration.
- Support multiple concurrent sessions.
- Thread-safe.

This module intentionally does NOT implement long-term memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterator
import threading
import uuid

__all__ = [
    "RuntimeContext",
    "ContextManager",
]


# =====================================================================
# Runtime Context
# =====================================================================


@dataclass(slots=True)
class RuntimeContext:
    """
    Represents one runtime execution context.
    """

    session_id: str

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    variables: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    config: dict[str, Any] = field(default_factory=dict)

    # ----------------------------------------------------------
    # Variable Access
    # ----------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.variables[key] = value

    def remove(self, key: str) -> None:
        self.variables.pop(key, None)

    def clear(self) -> None:
        self.variables.clear()

    # ----------------------------------------------------------
    # Python Protocols
    # ----------------------------------------------------------

    def __getitem__(self, key: str) -> Any:
        return self.variables[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.variables[key] = value

    def __delitem__(self, key: str) -> None:
        del self.variables[key]

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and key in self.variables

    def __len__(self) -> int:
        return len(self.variables)

    def __iter__(self) -> Iterator[str]:
        return iter(self.variables)

    def __repr__(self) -> str:
        return (
            f"RuntimeContext("
            f"session_id='{self.session_id}', "
            f"variables={len(self.variables)}, "
            f"metadata={len(self.metadata)})"
        )


# =====================================================================
# Context Manager
# =====================================================================


class ContextManager:
    """
    Thread-safe runtime context manager.
    """

    def __init__(self) -> None:

        self._contexts: dict[str, RuntimeContext] = {}

        self._current: str | None = None

        self._lock = threading.RLock()

    # ----------------------------------------------------------
    # Context Lifecycle
    # ----------------------------------------------------------

    def create(
        self,
        *,
        config: dict[str, Any] | None = None,
    ) -> RuntimeContext:
        """
        Create a new runtime context.

        The new context automatically becomes the active context.
        """

        with self._lock:

            session_id = str(uuid.uuid4())

            context = RuntimeContext(
                session_id=session_id,
                config=dict(config or {}),
            )

            self._contexts[session_id] = context

            self._current = session_id

            return context

    def current(self) -> RuntimeContext:
        """
        Return the active runtime context.
        """

        with self._lock:

            if self._current is None:
                raise RuntimeError("No active runtime context.")

            return self._contexts[self._current]

    def switch(self, session_id: str) -> RuntimeContext:
        """
        Switch active context.
        """

        with self._lock:

            if session_id not in self._contexts:
                raise KeyError(
                    f"Context '{session_id}' not found."
                )

            self._current = session_id

            return self._contexts[session_id]

    def get(self, session_id: str) -> RuntimeContext:
        """
        Retrieve a context by session id.
        """

        with self._lock:

            if session_id not in self._contexts:
                raise KeyError(
                    f"Context '{session_id}' not found."
                )

            return self._contexts[session_id]

    def remove(self, session_id: str) -> None:
        """
        Remove a runtime context.
        """

        with self._lock:

            if session_id not in self._contexts:
                return

            del self._contexts[session_id]

            if self._current == session_id:
                self._current = None

    def clear(self) -> None:
        """
        Remove all runtime contexts.
        """

        with self._lock:

            self._contexts.clear()

            self._current = None

    # ----------------------------------------------------------
    # Inspection
    # ----------------------------------------------------------

    def exists(self, session_id: str) -> bool:

        with self._lock:
            return session_id in self._contexts

    def sessions(self) -> list[str]:

        with self._lock:
            return list(self._contexts.keys())

    def contexts(self) -> list[RuntimeContext]:

        with self._lock:
            return list(self._contexts.values())

    def count(self) -> int:

        with self._lock:
            return len(self._contexts)

    # ----------------------------------------------------------
    # Python Protocols
    # ----------------------------------------------------------

    def __contains__(self, session_id: object) -> bool:

        return (
            isinstance(session_id, str)
            and self.exists(session_id)
        )

    def __len__(self) -> int:

        return self.count()

    def __iter__(self) -> Iterator[RuntimeContext]:

        with self._lock:
            return iter(tuple(self._contexts.values()))

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(contexts={len(self)})"
        )
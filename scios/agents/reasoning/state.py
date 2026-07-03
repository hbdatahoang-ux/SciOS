"""
SciOS Reasoning State
=====================

Shared runtime state for the SciOS reasoning subsystem.

The ReasoningState maintains reasoning history, execution context,
and runtime metadata independently of any specific reasoning
backend.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class ReasoningState:
    """
    Runtime state for the reasoning subsystem.

    Responsibilities
    ----------------
    - Track reasoning requests
    - Store execution history
    - Maintain shared reasoning context
    - Record reasoning results
    - Provide runtime statistics
    """

    def __init__(self) -> None:
        self.reset()

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def reset(self) -> None:
        """Reset the reasoning state."""

        self._created_at = datetime.now(timezone.utc)

        self._history: list[dict[str, Any]] = []

        self._results: list[dict[str, Any]] = []

        self._context: dict[str, Any] = {}

    # ==========================================================
    # Recording
    # ==========================================================

    def record(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Record a reasoning request.
        """

        entry = {
            "id": len(self._history) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query,
            "context": context or {},
        }

        self._history.append(entry)

        if context:
            self._context.update(context)

        return entry

    def record_result(
        self,
        result: dict[str, Any],
    ) -> None:
        """
        Record a reasoning result.
        """

        self._results.append(result)

    # ==========================================================
    # Context
    # ==========================================================

    def context(self) -> dict[str, Any]:
        """Return current reasoning context."""

        return dict(self._context)

    def update_context(
        self,
        values: dict[str, Any],
    ) -> None:
        """Merge values into the active context."""

        self._context.update(values)

    def clear_context(self) -> None:
        """Clear the active reasoning context."""

        self._context.clear()

    # ==========================================================
    # History
    # ==========================================================

    def history(self) -> list[dict[str, Any]]:
        """Return reasoning history."""

        return list(self._history)

    def latest(self) -> dict[str, Any] | None:
        """Return the most recent reasoning request."""

        if not self._history:
            return None

        return self._history[-1]

    def latest_result(self) -> dict[str, Any] | None:
        """Return the most recent reasoning result."""

        if not self._results:
            return None

        return self._results[-1]

    # ==========================================================
    # Statistics
    # ==========================================================

    def request_count(self) -> int:
        """Return the number of recorded reasoning requests."""

        return len(self._history)

    def result_count(self) -> int:
        """Return the number of recorded reasoning results."""

        return len(self._results)

    # ==========================================================
    # Status
    # ==========================================================

    def status(self) -> dict[str, Any]:
        """Return runtime status."""

        return {
            "component": "ReasoningState",
            "created_at": self._created_at.isoformat(),
            "requests": self.request_count(),
            "results": self.result_count(),
            "context_keys": len(self._context),
        }

    # ==========================================================
    # Dunder methods
    # ==========================================================

    def __len__(self) -> int:
        return self.request_count()

    def __repr__(self) -> str:
        return (
            "ReasoningState("
            f"requests={self.request_count()}, "
            f"results={self.result_count()}, "
            f"context={len(self._context)})"
        )
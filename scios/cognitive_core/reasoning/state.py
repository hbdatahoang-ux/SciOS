"""
SciOS Reasoning State
=====================

Manages lifecycle and records for reasoning operations.
"""

from __future__ import annotations

from typing import Any


class ReasoningState:
    """
    Tracks queries, contexts, and reasoning results.

    The state object is intentionally lightweight and contains no
    reasoning logic. It is responsible only for recording execution
    history and exposing immutable snapshots.
    """

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []
        self._results: list[dict[str, Any]] = []

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def reset(self) -> None:
        """
        Reset all recorded information.
        """

        self._records.clear()
        self._results.clear()

    # ==========================================================
    # Recording
    # ==========================================================

    def record(
        self,
        query: str,
        context: dict[str, Any],
    ) -> None:
        """
        Record a reasoning request.
        """

        self._records.append(
            {
                "query": query,
                "context": dict(context),
            }
        )

    def record_result(
        self,
        result: dict[str, Any],
    ) -> None:
        """
        Record a reasoning result.
        """

        self._results.append(dict(result))

    # ==========================================================
    # Accessors
    # ==========================================================

    def all_records(self) -> list[dict[str, Any]]:
        """
        Return a copy of all recorded requests.
        """

        return list(self._records)

    def all_results(self) -> list[dict[str, Any]]:
        """
        Return a copy of all recorded results.
        """

        return list(self._results)

    def snapshot(self) -> dict[str, Any]:
        """
        Return a complete immutable snapshot.

        An empty state is represented as an empty dictionary to
        preserve compatibility with legacy SciOS tests.
        """

        if not self._records and not self._results:
            return {}

        return {
            "records": self.all_records(),
            "results": self.all_results(),
        }

    def status(self) -> dict[str, Any]:
        """
        Return lightweight runtime statistics.
        """

        return {
            "records": len(self._records),
            "results": len(self._results),
        }

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __len__(self) -> int:
        """
        Number of recorded reasoning requests.
        """

        return len(self._records)

    def __bool__(self) -> bool:
        """
        Whether the state contains any information.
        """

        return bool(self._records or self._results)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"records={len(self._records)}, "
            f"results={len(self._results)})"
        )

    # ==========================================================
    # Compatibility
    # ==========================================================

    def __call__(self) -> dict[str, Any]:
        """
        Backward-compatible snapshot API.

        Allows both:

            engine.state()

        and:

            engine.state.status()
        """

        return self.snapshot()        
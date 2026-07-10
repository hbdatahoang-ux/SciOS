"""
SciOS Reasoning State
=====================

Manages lifecycle and records for reasoning operations.
"""

from __future__ import annotations
from typing import Any, Dict, List


class ReasoningState:
    """
    ReasoningState = Tracks queries, contexts, and results
    during reasoning pipeline execution.
    """

    def __init__(self) -> None:
        self._records: List[Dict[str, Any]] = []
        self._results: List[Dict[str, Any]] = []

    # ==========================================================
    # Lifecycle
    # ==========================================================
    def reset(self) -> None:
        """Reset all records and results."""
        self._records.clear()
        self._results.clear()

    # ==========================================================
    # Recording
    # ==========================================================
    def record(self, query: str, context: Dict[str, Any]) -> None:
        """Record a reasoning query and its context."""
        self._records.append({"query": query, "context": context})

    def record_result(self, result: Dict[str, Any]) -> None:
        """Record a reasoning result."""
        self._results.append(result)

    # ==========================================================
    # Accessors
    # ==========================================================
    def all_records(self) -> List[Dict[str, Any]]:
        """Return all recorded queries."""
        return list(self._records)

    def all_results(self) -> List[Dict[str, Any]]:
        """Return all recorded results."""
        return list(self._results)

    def status(self) -> Dict[str, Any]:
        """Return current state status."""
        return {
            "records": len(self._records),
            "results": len(self._results),
        }

    def __repr__(self) -> str:
        return f"ReasoningState(records={len(self._records)}, results={len(self._results)})"

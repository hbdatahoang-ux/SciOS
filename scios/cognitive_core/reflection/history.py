# scios/cognitive_core/reflection/history.py

"""
SciOS Reflection History
========================

ReflectionHistory stores and manages past reflection reports.
It allows retrieval, clearing, and inspection of reflection logs.
"""

from __future__ import annotations
from typing import Any, Dict, List


class ReflectionHistory:
    """
    ReflectionHistory maintains a list of reflection reports.
    """

    def __init__(self) -> None:
        self.entries: List[Dict[str, Any]] = []

    def store(self, report: Dict[str, Any]) -> None:
        """
        Store a reflection report in history.
        """
        self.entries.append(report)

    def latest(self) -> Dict[str, Any] | None:
        """
        Return the most recent reflection report.
        """
        if not self.entries:
            return None
        return self.entries[-1]

    def all(self) -> List[Dict[str, Any]]:
        """
        Return all reflection reports.
        """
        return list(self.entries)

    def count(self) -> int:
        """
        Return number of stored reflection reports.
        """
        return len(self.entries)

    def clear(self) -> None:
        """
        Clear all reflection history.
        """
        self.entries.clear()

    def __repr__(self) -> str:
        return f"<ReflectionHistory entries={len(self.entries)}>"

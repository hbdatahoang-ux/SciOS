# scios/cognitive_core/reflection/recorder.py

"""
SciOS Reflection Recorder
=========================

ReflectionRecorder logs events and messages during the reflection process.
It provides a simple mechanism to track progress, debug issues,
and review reflection activity.
"""

from __future__ import annotations
from typing import List


class ReflectionRecorder:
    """
    ReflectionRecorder maintains a log of reflection events.
    """

    def __init__(self) -> None:
        self.logs: List[str] = []

    def log(self, message: str) -> None:
        """
        Append a message to the reflection log.
        """
        self.logs.append(message)

    def latest(self) -> str | None:
        """
        Return the most recent log entry.
        """
        if not self.logs:
            return None
        return self.logs[-1]

    def all(self) -> List[str]:
        """
        Return all log entries.
        """
        return list(self.logs)

    def clear(self) -> None:
        """
        Clear all log entries.
        """
        self.logs.clear()

    def __repr__(self) -> str:
        return f"<ReflectionRecorder logs={len(self.logs)}>"

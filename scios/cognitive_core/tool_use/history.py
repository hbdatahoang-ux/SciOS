# scios/cognitive_core/tool_use/history.py

"""
SciOS Cognitive Core Tool History
=================================

Semantic history of tool-use interactions.

ToolHistory records:
- ToolRequest: cognitive intent
- ToolResponse: cognitive interpretation
- timestamp: interaction time

ToolHistory MUST NOT own or execute runtime tools.
Execution outcomes are outside the responsibility of this semantic history.
"""

from __future__ import annotations

import time
from typing import Any

from .request import ToolRequest
from .response import ToolResponse

__all__ = (
    "ToolHistoryEntry",
    "ToolHistory",
)


class ToolHistoryEntry:
    """
    A single semantic tool-use interaction.

    The entry keeps the original ToolRequest and ToolResponse objects
    rather than duplicating their fields as raw dictionaries.
    """

    def __init__(
        self,
        request: ToolRequest,
        response: ToolResponse,
        *,
        timestamp: float | None = None,
    ) -> None:
        if not isinstance(request, ToolRequest):
            raise TypeError("request must be a ToolRequest")

        if not isinstance(response, ToolResponse):
            raise TypeError("response must be a ToolResponse")

        self.request = request
        self.response = response
        self.timestamp = time.time() if timestamp is None else float(timestamp)

    @property
    def tool(self) -> str:
        """Return the semantic tool name from the request."""
        return self.request.tool

    def to_dict(self) -> dict[str, Any]:
        """Serialize the history entry to a plain dictionary."""
        return {
            "tool": self.request.tool,
            "request": self.request.to_dict(),
            "response": self.response.to_dict(),
            "timestamp": self.timestamp,
        }

    def __repr__(self) -> str:
        return (
            f"<ToolHistoryEntry "
            f"tool={self.request.tool!r} "
            f"status={self.response.status!r} "
            f"at={self.timestamp}>"
        )


class ToolHistory:
    """
    In-memory history of semantic tool-use interactions.

    ToolHistory is a Cognitive Core artifact. It does not execute tools,
    resolve executable Tool instances, enforce runtime policy, or collect
    runtime execution metrics.
    """

    def __init__(self) -> None:
        self.entries: list[ToolHistoryEntry] = []

    def log(
        self,
        request: ToolRequest,
        response: ToolResponse,
        *,
        timestamp: float | None = None,
    ) -> ToolHistoryEntry:
        """
        Record a semantic tool-use interaction.

        Returns the newly created history entry.
        """
        entry = ToolHistoryEntry(
            request,
            response,
            timestamp=timestamp,
        )
        self.entries.append(entry)
        return entry

    def list(self) -> list[dict[str, Any]]:
        """Return the complete history as dictionaries."""
        return [entry.to_dict() for entry in self.entries]

    def filter_by_tool(self, tool: str) -> list[dict[str, Any]]:
        """Return history entries associated with the given tool name."""
        if not isinstance(tool, str):
            return []

        tool = tool.strip()

        if not tool:
            return []

        return [
            entry.to_dict()
            for entry in self.entries
            if entry.tool == tool
        ]

    def clear(self) -> None:
        """Remove all history entries."""
        self.entries.clear()

    def __len__(self) -> int:
        return len(self.entries)

    def __repr__(self) -> str:
        return f"<ToolHistory entries={len(self.entries)}>"
"""
SciOS Cognitive ToolUse Request

Canonical semantic request for Cognitive ToolUse.

Contract:
    tool
    action
    params
    metadata

`action` is the canonical semantic action.
It is not a Runtime Tool operation identifier.
"""

from __future__ import annotations

from typing import Any


__all__ = ["ToolRequest"]


class ToolRequest:
    """Canonical request for a Cognitive Tool invocation."""

    def __init__(
        self,
        tool: str,
        action: str,
        params: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not isinstance(tool, str) or not tool.strip():
            raise ValueError("Tool name cannot be empty")

        if not isinstance(action, str) or not action.strip():
            raise ValueError("Tool action cannot be empty")

        if params is not None and not isinstance(params, dict):
            raise TypeError("Tool params must be a dictionary")

        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError("Tool metadata must be a dictionary")

        self.tool = tool.strip()
        self.action = action.strip()
        self.params = dict(params) if params is not None else {}
        self.metadata = dict(metadata) if metadata is not None else {}

    @property
    def parameters(self) -> dict[str, Any]:
        """Compatibility alias for params."""
        return self.params

    @parameters.setter
    def parameters(self, value: dict[str, Any]) -> None:
        if not isinstance(value, dict):
            raise TypeError("Tool parameters must be a dictionary")

        self.params = dict(value)

    def to_dict(self) -> dict[str, Any]:
        """Return canonical dictionary representation."""
        return {
            "tool": self.tool,
            "action": self.action,
            "params": dict(self.params),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ToolRequest:
        """Create a request from a dictionary."""
        if not isinstance(data, dict):
            raise TypeError("Tool request data must be a dictionary")

        params = data.get("params")

        if params is None:
            params = data.get("parameters", {})

        return cls(
            tool=data.get("tool", ""),
            action=data.get("action", ""),
            params=params,
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_context(cls, context: dict[str, Any]) -> ToolRequest:
        """
        Create a request from pipeline context.

        `action` is canonical.
        `operation` is accepted only as legacy compatibility input.
        """
        if not isinstance(context, dict):
            raise TypeError("Tool context must be a dictionary")

        action = context.get("action")

        if not action:
            action = context.get("operation", "")

        return cls(
            tool=context.get("tool", ""),
            action=action,
            params=context.get("params", {}),
            metadata=context.get("metadata", {}),
        )

    def update_metadata(self, **kwargs: Any) -> None:
        """Update request metadata."""
        self.metadata.update(kwargs)

    def __repr__(self) -> str:
        return (
            f"<ToolRequest "
            f"tool={self.tool!r} "
            f"action={self.action!r}>"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ToolRequest):
            return NotImplemented

        return (
            self.tool == other.tool
            and self.action == other.action
            and self.params == other.params
            and self.metadata == other.metadata
        )

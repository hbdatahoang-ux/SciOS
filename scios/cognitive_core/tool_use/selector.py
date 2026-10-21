"""
SciOS Cognitive Core Tool Selector
==================================

Selects a semantic tool capability for a cognitive ToolRequest.

Architectural boundary
----------------------

    Cognitive reasoning
          |
          v
    ToolSelector
          |
          v
    semantic tool identity
          |
          v
    ToolRequest
          |
          |  explicit boundary
          v
    Runtime ToolRouter

ToolSelector MUST NOT:
    - own a ToolRegistry
    - resolve executable Tool instances
    - execute tools
    - invoke Tool.validate()
    - own ToolExecutor / ToolSandbox / ToolPolicy
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .request import ToolRequest


__all__ = ["ToolSelector"]


class ToolSelector:
    """
    Select a semantic tool identity for a cognitive tool request.

    The selector operates entirely in the Cognitive layer.

    It does not resolve executable runtime Tool objects and does not
    perform runtime authorization, execution, sandboxing, or policy
    enforcement.
    """

    def __init__(
        self,
        capabilities: Iterable[str] | Mapping[str, Any] | None = None,
    ) -> None:
        """
        Create a semantic tool selector.

        Parameters
        ----------
        capabilities:
            Optional collection or mapping of known semantic tool names.

        Notes
        -----
        The values are cognitive capability identifiers only. They are
        not executable Tool instances and must not be backed by a
        Runtime ToolRegistry.
        """

        if capabilities is None:
            self._capabilities: dict[str, Any] = {}
        elif isinstance(capabilities, Mapping):
            self._capabilities = {
                str(name): value
                for name, value in capabilities.items()
            }
        else:
            self._capabilities = {
                str(name): None
                for name in capabilities
            }

    # ==========================================================
    # Selection
    # ==========================================================

    def select(
        self,
        request: ToolRequest | Mapping[str, Any],
    ) -> str | None:
        """
        Select the semantic tool identified by ``request``.

        Returns
        -------
        str | None
            The selected semantic tool name, or ``None`` when the
            request cannot be selected.

        No executable runtime object is returned.
        """

        if isinstance(request, ToolRequest):
            tool_name = request.tool

        elif isinstance(request, Mapping):
            tool_name = request.get("tool")

        else:
            return None

        if not isinstance(tool_name, str):
            return None

        tool_name = tool_name.strip()

        if not tool_name:
            return None

        if self._capabilities and tool_name not in self._capabilities:
            return None

        return tool_name

    # ==========================================================
    # Capability inspection
    # ==========================================================

    def available_tools(self) -> tuple[str, ...]:
        """
        Return known semantic tool capability names.

        These are identifiers only, not executable Tool instances.
        """

        return tuple(self._capabilities.keys())

    def has(self, name: str) -> bool:
        """
        Return whether a semantic tool capability is known.
        """

        if not isinstance(name, str):
            return False

        name = name.strip()

        if not name:
            return False

        if not self._capabilities:
            return True

        return name in self._capabilities

    # ==========================================================
    # Request construction
    # ==========================================================

    def request(
        self,
        tool: str,
        action: str,
        *,
        params: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ToolRequest:
        """
        Construct a canonical Cognitive ToolRequest.

        This method creates intent only. It does not execute anything.
        """

        return ToolRequest(
            tool=tool,
            action=action,
            params=dict(params or {}),
            metadata=dict(metadata or {}),
        )

    # ==========================================================
    # Protocol
    # ==========================================================

    def __contains__(self, name: object) -> bool:
        if not isinstance(name, str):
            return False

        return self.has(name)

    def __repr__(self) -> str:
        return (
            f"<ToolSelector "
            f"capabilities={len(self._capabilities)}>"
        )
"""
SciOS Cognitive Core Tool Selector
==================================

Selects the appropriate Tool for a request.

Design
------
ToolSelector is registry-aware:

    selector = ToolSelector(registry)
    tool = selector.select(request)

Selection flow:

    request
       |
       v
    tool name
       |
       v
    ToolRegistry.get()
       |
       +---- not found ----> None
       |
       v
    Tool.validate(request)
       |
       +---- invalid ------> None
       |
       v
      Tool

The implementation also preserves compatibility with the older
candidate-based API:

    selector.select(candidates, request)

Python 3.11+
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, overload

from scios.cognitive_core.tool_use.base import Tool
from scios.cognitive_core.tool_use.registry import ToolRegistry


__all__ = [
    "ToolSelector",
]


class ToolSelector:
    """
    Select a Tool for a request.

    Primary API
    -----------
    selector = ToolSelector(registry)
    tool = selector.select(request)

    The selector:

    1. extracts the requested tool name from ``request["tool"]``;
    2. resolves the tool through ``ToolRegistry``;
    3. validates the request using ``tool.validate(request)``;
    4. returns the tool when valid;
    5. returns ``None`` when the request cannot be satisfied.

    Compatibility API
    ------------------
    The legacy form

        selector.select(candidates, request)

    is also supported. This keeps older callers functional while the
    registry-based API becomes the canonical interface.
    """

    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:
        """
        Create a ToolSelector bound to a ToolRegistry.

        Parameters
        ----------
        registry:
            Registry used to resolve tools by name.

        Raises
        ------
        TypeError
            If ``registry`` is not a ToolRegistry instance.
        """

        if not isinstance(registry, ToolRegistry):
            raise TypeError(
                "registry must be an instance of ToolRegistry"
            )

        self.registry = registry

    # ==========================================================
    # Primary Selection API
    # ==========================================================

    @overload
    def select(
        self,
        request: Dict[str, Any],
    ) -> Optional[Tool]:
        ...

    @overload
    def select(
        self,
        candidates: Iterable[Tool],
        request: Dict[str, Any],
    ) -> Optional[Tool]:
        ...

    def select(
        self,
        first: Dict[str, Any] | Iterable[Tool],
        second: Optional[Dict[str, Any]] = None,
    ) -> Optional[Tool]:
        """
        Select a tool.

        Canonical form
        --------------
        ``select(request)``

        Compatibility form
        -------------------
        ``select(candidates, request)``

        Returns
        -------
        Optional[Tool]
            The selected and validated tool, or ``None``.
        """

        # ------------------------------------------------------
        # Canonical registry-based API
        # ------------------------------------------------------

        if second is None:

            request = first

            if not isinstance(request, dict):
                return None

            return self._select_from_registry(request)

        # ------------------------------------------------------
        # Legacy candidate-based API
        # ------------------------------------------------------

        candidates = first
        request = second

        if not isinstance(request, dict):
            return None

        return self._select_from_candidates(
            candidates,
            request,
        )

    # ==========================================================
    # Registry Selection
    # ==========================================================

    def _select_from_registry(
        self,
        request: Dict[str, Any],
    ) -> Optional[Tool]:
        """
        Resolve and validate a tool through the registry.
        """

        tool_name = request.get("tool")

        if not isinstance(tool_name, str):
            return None

        tool_name = tool_name.strip()

        if not tool_name:
            return None

        tool = self.registry.get(tool_name)

        if tool is None:
            return None

        if not self._validate(tool, request):
            return None

        return tool

    # ==========================================================
    # Candidate Selection
    # ==========================================================

    def _select_from_candidates(
        self,
        candidates: Iterable[Tool],
        request: Dict[str, Any],
    ) -> Optional[Tool]:
        """
        Select a tool from an explicit candidate collection.

        This method exists for backward compatibility with the
        original ToolSelector contract.
        """

        if candidates is None:
            return None

        try:
            candidate_list: List[Tool] = list(candidates)
        except TypeError:
            return None

        if not candidate_list:
            return None

        requested_name = request.get("tool")

        # If a tool name is supplied, prefer an exact name match.
        if isinstance(requested_name, str):
            requested_name = requested_name.strip()

            if requested_name:
                for tool in candidate_list:

                    if getattr(
                        tool,
                        "name",
                        None,
                    ) != requested_name:
                        continue

                    if self._validate(
                        tool,
                        request,
                    ):
                        return tool

                return None

        # Without a requested tool name, select the first valid
        # candidate.
        for tool in candidate_list:

            if self._validate(
                tool,
                request,
            ):
                return tool

        return None

    # ==========================================================
    # Validation
    # ==========================================================

    @staticmethod
    def _validate(
        tool: Tool,
        request: Dict[str, Any],
    ) -> bool:
        """
        Validate a request against a Tool.

        Validation failures are treated as selection failures and
        therefore return ``False`` rather than propagating ordinary
        validation exceptions.
        """

        if not isinstance(tool, Tool):
            return False

        try:
            return bool(
                tool.validate(request)
            )

        except Exception:
            return False

    # ==========================================================
    # Introspection
    # ==========================================================

    def available_tools(self) -> Dict[str, str]:
        """
        Return registered tools and their descriptions.
        """

        return self.registry.list_tools()

    def get(
        self,
        name: str,
    ) -> Optional[Tool]:
        """
        Resolve a tool directly from the registry.
        """

        if not isinstance(name, str):
            return None

        name = name.strip()

        if not name:
            return None

        return self.registry.get(name)

    # ==========================================================
    # Protocol
    # ==========================================================

    def __repr__(self) -> str:
        """
        Return a concise selector representation.
        """

        return (
            f"<ToolSelector "
            f"registry={self.registry!r}>"
        )
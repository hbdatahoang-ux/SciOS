"""
SciOS Tool Request
==================

Standardized tool invocation request.

Features:
- Tool name validation
- Action validation
- Parameters
- Metadata
- Context conversion
- Serialization

Python 3.11+
"""

from __future__ import annotations

from typing import Any, Dict, Optional


__all__ = [
    "ToolRequest",
]


class ToolRequest:
    """
    ToolRequest is the canonical structure
    for every tool execution request.
    """

    def __init__(
        self,
        tool: str,
        action: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        # ==================================================
        # Validation
        # ==================================================

        if not isinstance(
            tool,
            str,
        ) or not tool.strip():

            raise ValueError(
                "Tool name cannot be empty"
            )


        if not isinstance(
            action,
            str,
        ) or not action.strip():

            raise ValueError(
                "Tool action cannot be empty"
            )


        self.tool = tool.strip()

        self.action = action.strip()


        self.params: Dict[str, Any] = (
            params.copy()
            if params
            else {}
        )


        self.metadata: Dict[str, Any] = (
            metadata.copy()
            if metadata
            else {}
        )


    # ======================================================
    # Properties
    # ======================================================

    @property
    def parameters(
        self,
    ) -> Dict[str, Any]:
        """
        Compatibility alias.

        Some pipelines use `parameters`
        instead of `params`.
        """

        return self.params


    @parameters.setter
    def parameters(
        self,
        value: Dict[str, Any],
    ) -> None:

        self.params = (
            value.copy()
            if value
            else {}
        )


    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert request into dictionary.
        """

        return {

            "tool":
                self.tool,

            "action":
                self.action,

            "params":
                self.params.copy(),

            "metadata":
                self.metadata.copy(),

        }


    # ======================================================
    # Constructors
    # ======================================================

    @classmethod
    def from_context(
        cls,
        context: Dict[str, Any],
    ) -> "ToolRequest":
        """
        Build ToolRequest from pipeline context.
        """

        return cls(

            tool=context.get(
                "tool",
                "",
            ),

            action=(
                context.get(
                    "action"
                )
                or context.get(
                    "operation",
                    "",
                )
            ),

            params=context.get(
                "params",
                {},
            ),

            metadata=context.get(
                "metadata",
                {},
            ),

        )


    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "ToolRequest":
        """
        Deserialize from dictionary.
        """

        return cls(

            tool=data.get(
                "tool",
                "",
            ),

            action=data.get(
                "action",
                "",
            ),

            params=data.get(
                "params",
                data.get(
                    "parameters",
                    {},
                ),
            ),

            metadata=data.get(
                "metadata",
                {},
            ),

        )


    # ======================================================
    # Utilities
    # ======================================================

    def update_metadata(
        self,
        **kwargs: Any,
    ) -> None:
        """
        Update request metadata.
        """

        self.metadata.update(
            kwargs
        )


    def __repr__(
        self,
    ) -> str:

        return (
            f"<ToolRequest "
            f"tool={self.tool!r} "
            f"action={self.action!r}>"
        )


    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            ToolRequest,
        ):
            return False


        return (
            self.tool == other.tool
            and
            self.action == other.action
            and
            self.params == other.params
            and
            self.metadata == other.metadata
        )
"""
SciOS Runtime Tool Registry
===========================

Central registry for runtime tools.

Python 3.11+
"""

from __future__ import annotations


from typing import (
    Any,
)


from .base import Tool



__all__ = [
    "ToolRegistry",
]



# ==========================================================
# Tool Registry
# ==========================================================


class ToolRegistry:
    """
    Runtime tool manager.

    Responsibilities:

    - register tools
    - remove tools
    - lookup tools
    - lifecycle management
    - diagnostics
    """



    # ======================================================
    # Construction
    # ======================================================


    def __init__(self) -> None:


        self._tools: dict[str, Tool] = {}



    # ======================================================
    # Properties
    # ======================================================


    @property
    def tools(
        self,
    ) -> dict[str, Tool]:

        return self._tools



    @property
    def count(
        self,
    ) -> int:

        return len(
            self._tools
        )



    # ======================================================
    # Register
    # ======================================================


    def register(
        self,
        tool: Tool,
    ) -> Tool:
        """
        Register new tool.
        """


        if not isinstance(
            tool,
            Tool,
        ):

            raise TypeError(
                "Only Tool instances can be registered"
            )



        name = tool.name



        if name in self._tools:

            raise ValueError(
                f"Tool already registered: {name}"
            )



        tool.initialize()


        self._tools[name] = tool


        return tool



    # ======================================================
    # Unregister
    # ======================================================


    def unregister(
        self,
        name: str,
    ) -> Tool | None:
        """
        Remove tool.
        """


        tool = self._tools.pop(
            name,
            None,
        )


        if tool:

            tool.shutdown()



        return tool



    # ======================================================
    # Lookup
    # ======================================================


    def get(
        self,
        name: str,
        default=None,
    ) -> Tool | None:
        """
        Get tool by name.
        """


        return self._tools.get(
            name,
            default,
        )



    def require(
        self,
        name: str,
    ) -> Tool:
        """
        Get tool or raise.
        """


        tool = self.get(
            name
        )


        if tool is None:

            raise KeyError(
                f"Unknown tool: {name}"
            )


        return tool



    def exists(
        self,
        name: str,
    ) -> bool:

        return name in self._tools



    # ======================================================
    # Execution Helpers
    # ======================================================


    def enable(
        self,
        name: str,
    ) -> None:


        self.require(
            name
        ).enable()



    def disable(
        self,
        name: str,
    ) -> None:


        self.require(
            name
        ).disable()



    # ======================================================
    # Collection
    # ======================================================


    def list(
        self,
    ) -> list[str]:

        return list(
            self._tools.keys()
        )



    def values(
        self,
    ) -> list[Tool]:

        return list(
            self._tools.values()
        )



    def clear(
        self,
    ) -> None:
        """
        Shutdown and remove all tools.
        """


        for tool in self._tools.values():

            tool.shutdown()



        self._tools.clear()



    # ======================================================
    # Diagnostics
    # ======================================================


    def status(
        self,
    ) -> dict[str, Any]:

        return {

            "count":
                self.count,


            "tools":
                [
                    tool.to_dict()
                    for tool in self._tools.values()
                ],

        }



    def health(
        self,
    ) -> dict[str, Any]:

        return {

            name:
                tool.health()

            for name, tool
            in self._tools.items()

        }



    # ======================================================
    # Protocol
    # ======================================================


    def __len__(
        self,
    ) -> int:

        return self.count



    def __contains__(
        self,
        name: str,
    ) -> bool:

        return self.exists(
            name
        )



    def __iter__(
        self,
    ):

        return iter(
            self._tools.values()
        )



    def __repr__(
        self,
    ) -> str:

        return (
            "ToolRegistry("
            f"tools={self.list()!r}"
            ")"
        )
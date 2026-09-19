"""
SciOS Tool Response
===================

Standard response object for tool execution.

Supports:
- Tool identity
- success/error factory API
- result payload
- error message
- metadata
- serialization

Python 3.11+
"""

from __future__ import annotations

from typing import Any, Dict, Optional


__all__ = [
    "ToolResponse",
]


class ToolResponse:
    """
    Canonical result returned from tools.
    """


    VALID_STATUSES = {
        "success",
        "error",
    }


    def __init__(
        self,
        tool: str,
        status: str,
        result: Any = None,
        message: Optional[str] = None,
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
            status,
            str,
        ):

            raise ValueError(
                "Status must be string"
            )


        status = status.strip().lower()


        if status not in self.VALID_STATUSES:

            raise ValueError(
                f"Invalid status: {status}"
            )


        self.tool = tool.strip()

        self.status = status

        self.result = result

        self.message = message


        self.metadata = (
            metadata.copy()
            if metadata
            else {}
        )


    # ======================================================
    # Factory APIs
    # ======================================================

    @classmethod
    def success(
        cls,
        tool: str,
        result: Any = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> "ToolResponse":
        """
        Create successful response.
        """

        return cls(

            tool=tool,

            status="success",

            result=result,

            metadata=metadata,

        )



    @classmethod
    def error(
        cls,
        tool: str,
        message: str,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> "ToolResponse":
        """
        Create error response.
        """

        return cls(

            tool=tool,

            status="error",

            message=message,

            metadata=metadata,

        )



    # ======================================================
    # State helpers
    # ======================================================

    def is_success(
        self,
    ) -> bool:

        return (
            self.status
            ==
            "success"
        )


    def is_error(
        self,
    ) -> bool:

        return (
            self.status
            ==
            "error"
        )


    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "tool":
                self.tool,

            "status":
                self.status,

            "result":
                self.result,

            "message":
                self.message,

            "metadata":
                self.metadata.copy(),

        }



    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "ToolResponse":

        return cls(

            tool=data.get(
                "tool",
                "",
            ),

            status=data.get(
                "status",
                "",
            ),

            result=data.get(
                "result",
            ),

            message=data.get(
                "message",
            ),

            metadata=data.get(
                "metadata",
                {},
            ),

        )


    # ======================================================
    # Protocol
    # ======================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"<ToolResponse "
            f"tool={self.tool!r} "
            f"status={self.status!r}>"

        )


    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            ToolResponse,
        ):

            return False


        return (

            self.tool
            ==
            other.tool

            and

            self.status
            ==
            other.status

            and

            self.result
            ==
            other.result

            and

            self.message
            ==
            other.message

            and

            self.metadata
            ==
            other.metadata

        )
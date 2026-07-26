"""
SciOS Runtime Tool Result
=========================

Canonical result object returned by Tool execution.

Python 3.11+
"""

from __future__ import annotations


from dataclasses import (
    dataclass,
    field,
)

from datetime import (
    datetime,
    timezone,
)

from typing import (
    Any,
)


__all__ = [
    "ToolResult",
]



# ==========================================================
# Helpers
# ==========================================================


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()



# ==========================================================
# ToolResult
# ==========================================================


@dataclass(slots=True)
class ToolResult:
    """
    Result returned from tool execution.

    Lifecycle:

        running
            |
        +---+---+
        |       |
     success  failed
    """


    # ------------------------------------------------------
    # Status
    # ------------------------------------------------------

    success: bool = False


    # ------------------------------------------------------
    # Value
    # ------------------------------------------------------

    value: Any = None


    # ------------------------------------------------------
    # Error
    # ------------------------------------------------------

    error: Exception | None = None



    # ------------------------------------------------------
    # Metadata
    # ------------------------------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


    # ------------------------------------------------------
    # Timing
    # ------------------------------------------------------

    created_at: str = field(
        default_factory=utc_now
    )



    # ======================================================
    # Factory
    # ======================================================


    @classmethod
    def ok(
        cls,
        value: Any = None,
        *,
        metadata=None,
    ) -> "ToolResult":

        return cls(
            success=True,
            value=value,
            metadata=dict(
                metadata or {}
            ),
        )



    @classmethod
    def fail(
        cls,
        error: Exception,
        *,
        metadata=None,
    ) -> "ToolResult":

        return cls(
            success=False,
            error=error,
            metadata=dict(
                metadata or {}
            ),
        )



    # ======================================================
    # Properties
    # ======================================================


    @property
    def failed(self) -> bool:

        return not self.success



    @property
    def message(self):

        if self.error:

            return str(
                self.error
            )

        return None



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "success":
                self.success,


            "value":
                self.value,


            "error":
                (
                    str(self.error)
                    if self.error
                    else None
                ),


            "metadata":
                dict(
                    self.metadata
                ),


            "created_at":
                self.created_at,

        }



    # ======================================================
    # Protocol
    # ======================================================


    def __bool__(self):

        return self.success



    def __repr__(self):

        return (
            "ToolResult("
            f"success={self.success}, "
            f"value={self.value!r}"
            ")"
        )
"""
SciOS Runtime Tool Interface
============================

Base contract for all runtime tools.

Every runtime tool must inherit Tool
and implement execute().

Architecture:

Tool
 |
 +-- validate()
 |
 +-- execute()
 |
 +-- run()
 |
 +-- ToolResult


Python 3.11+
"""

from __future__ import annotations


from abc import (
    ABC,
    abstractmethod,
)


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
    ClassVar,
)


from uuid import (
    uuid4,
)


from .result import ToolResult



__all__ = [
    "Tool",
]



# ==========================================================
# Helpers
# ==========================================================


def utc_now() -> str:
    """
    UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()



# ==========================================================
# Tool Base Class
# ==========================================================


@dataclass(slots=True)
class Tool(
    ABC
):
    """
    Abstract SciOS Runtime Tool.

    Example:

        class EchoTool(Tool):

            NAME = "echo"


            def execute(
                self,
                text,
            ):
                return text

    """



    # ======================================================
    # Class Metadata
    # ======================================================


    NAME: ClassVar[str] = (
        "unnamed-tool"
    )


    DESCRIPTION: ClassVar[str] = (
        ""
    )


    VERSION: ClassVar[str] = (
        "0.1.0"
    )



    # ======================================================
    # Runtime Identity
    # ======================================================


    id: str = field(
        default_factory=lambda:
            str(uuid4())
    )



    created_at: str = field(
        default_factory=utc_now
    )



    # ======================================================
    # Runtime State
    # ======================================================


    enabled: bool = True



    executions: int = 0



    failures: int = 0



    metadata: dict[str, Any] = field(
        default_factory=dict
    )



    # ======================================================
    # Identity API
    # ======================================================


    @property
    def name(
        self,
    ) -> str:

        return self.NAME



    @property
    def description(
        self,
    ) -> str:

        return self.DESCRIPTION



    @property
    def version(
        self,
    ) -> str:

        return self.VERSION



    # ======================================================
    # Lifecycle
    # ======================================================


    def initialize(
        self,
    ) -> None:
        """
        Called before first execution.
        """

        return None



    def shutdown(
        self,
    ) -> None:
        """
        Cleanup hook.
        """

        return None



    def enable(
        self,
    ) -> None:

        self.enabled = True



    def disable(
        self,
    ) -> None:

        self.enabled = False



    # ======================================================
    # Validation
    # ======================================================


    def validate(
        self,
        **kwargs: Any,
    ) -> bool:
        """
        Input validation hook.

        Override for custom schema.
        """

        return True



    # ======================================================
    # Permission Hook
    # ======================================================


    def required_permissions(
        self,
    ) -> set[str]:
        """
        Permissions required by tool.

        Used by ToolPolicy.
        """

        return set()



    # ======================================================
    # Execution Contract
    # ======================================================


    @abstractmethod
    def execute(
        self,
        **kwargs: Any,
    ) -> Any:
        """
        Core tool implementation.

        Must be overridden.

        Can return:

        - raw value
        - ToolResult
        """

        raise NotImplementedError



    # ======================================================
    # Safe Execution Wrapper
    # ======================================================


    def run(
        self,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Standard execution wrapper.
        """



        if not self.enabled:

            return ToolResult.fail(
                RuntimeError(
                    "Tool disabled"
                )
            )



        if not self.validate(
            **kwargs
        ):

            return ToolResult.fail(
                ValueError(
                    "Invalid tool input"
                )
            )



        try:


            result = self.execute(
                **kwargs
            )


            self.executions += 1



            if isinstance(
                result,
                ToolResult,
            ):

                return result



            return ToolResult.ok(
                result
            )



        except Exception as exc:


            self.failures += 1


            return ToolResult.fail(
                exc
            )



    # ======================================================
    # Schema
    # ======================================================


    def schema(
        self,
    ) -> dict[str, Any]:
        """
        Input schema description.

        Override when needed.
        """

        return {}



    # ======================================================
    # Diagnostics
    # ======================================================


    def health(
        self,
    ) -> dict[str, Any]:

        return {

            "id":
                self.id,


            "name":
                self.name,


            "version":
                self.version,


            "enabled":
                self.enabled,


            "executions":
                self.executions,


            "failures":
                self.failures,

        }



    def stats(
        self,
    ) -> dict[str, Any]:

        return {

            "executions":
                self.executions,


            "failures":
                self.failures,


            "success_rate":
                (
                    (
                        self.executions
                        -
                        self.failures
                    )
                    /
                    self.executions
                    if self.executions
                    else 0.0
                ),

        }



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "id":
                self.id,


            "name":
                self.name,


            "description":
                self.description,


            "version":
                self.version,


            "enabled":
                self.enabled,


            "metadata":
                dict(
                    self.metadata
                ),


            "executions":
                self.executions,


            "failures":
                self.failures,


            "created_at":
                self.created_at,

        }



    # ======================================================
    # Callable Interface
    # ======================================================


    def __call__(
        self,
        **kwargs: Any,
    ) -> ToolResult:

        return self.run(
            **kwargs
        )



    # ======================================================
    # Protocol
    # ======================================================


    def __repr__(
        self,
    ) -> str:

        return (

            "Tool("
            f"name={self.name!r}, "
            f"version={self.version!r}, "
            f"enabled={self.enabled}"
            ")"

        )
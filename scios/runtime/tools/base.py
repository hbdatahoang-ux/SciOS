"""
SciOS Runtime Tool Interface
============================

Base contract for all runtime tools.

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


from .result import ToolResult



__all__ = [
    "Tool",
]



# ==========================================================
# Helpers
# ==========================================================


def utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()



# ==========================================================
# Tool Interface
# ==========================================================


@dataclass(slots=True)
class Tool(
    ABC
):
    """
    Abstract SciOS Tool contract.

    Every tool must implement:

        execute()

    Example:

        class CalculatorTool(Tool):

            NAME = "calculator"

            def execute(self, **kwargs):
                return 1 + 1
    """


    # ------------------------------------------------------
    # Class Metadata
    # ------------------------------------------------------

    NAME: ClassVar[str] = (
        "unnamed-tool"
    )


    DESCRIPTION: ClassVar[str] = (
        ""
    )


    VERSION: ClassVar[str] = (
        "0.1.0"
    )



    # ------------------------------------------------------
    # Runtime State
    # ------------------------------------------------------

    enabled: bool = True


    metadata: dict[str, Any] = field(
        default_factory=dict
    )


    created_at: str = field(
        default_factory=utc_now
    )


    executions: int = 0



    # ======================================================
    # Identity
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
        Optional initialization hook.
        """

        return None



    def shutdown(
        self,
    ) -> None:
        """
        Optional cleanup hook.
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
        Validate execution input.

        Override when tool requires
        strict schema.
        """

        return True



    # ======================================================
    # Execution Contract
    # ======================================================


    @abstractmethod
    def execute(
        self,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Execute tool.

        Must return ToolResult.
        """

        raise NotImplementedError



    # ======================================================
    # Safe Run Wrapper
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
        Tool input schema.

        Override for structured tools.
        """

        return {}



    # ======================================================
    # Diagnostics
    # ======================================================


    def health(
        self,
    ) -> dict[str, Any]:

        return {

            "name":
                self.name,

            "version":
                self.version,

            "enabled":
                self.enabled,

            "executions":
                self.executions,

        }



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

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

        }



    # ======================================================
    # Protocol
    # ======================================================


    def __call__(
        self,
        **kwargs: Any,
    ) -> ToolResult:

        return self.run(
            **kwargs
        )



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
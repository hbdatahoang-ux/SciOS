"""
SciOS Tool Use Stage

Tool execution cognitive stage.
"""

from __future__ import annotations


class ToolUseStage:
    """
    Cognitive pipeline stage for tool execution.
    """

    name = "tooluse"


    def __init__(
        self,
    ) -> None:

        pass


    def run(
        self,
        raw_input: str,
    ) -> dict:

        """
        Execute tool request.

        Examples:

            calculate 2+2
            1+1
        """

        expression = (
            raw_input
            .replace(
                "calculate",
                "",
            )
            .strip()
        )


        try:

            result = eval(
                expression,
                {
                    "__builtins__": {},
                },
            )


            return {
                "output": str(result)
            }


        except Exception:

            return {
                "output": None
            }
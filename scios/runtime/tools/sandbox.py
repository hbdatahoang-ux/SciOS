"""
SciOS Runtime Tool Sandbox
==========================

Execution isolation layer for runtime tools.

Python 3.11+

Features:
- timeout control
- exception isolation
- result normalization
- cross-platform execution
"""

from __future__ import annotations


from concurrent.futures import (
    ThreadPoolExecutor,
    TimeoutError as FutureTimeoutError,
)

from typing import (
    Any,
)


from .policy import ToolPolicy
from .result import ToolResult


__all__ = [
    "ToolSandbox",
]



class ToolSandbox:
    """
    Safe execution environment for tools.

    Responsibilities:

    - validate policy
    - execute tool
    - catch exceptions
    - enforce timeout
    """



    # ======================================================
    # Construction
    # ======================================================


    def __init__(
        self,
        *,
        policy: ToolPolicy | None = None,
    ) -> None:


        self._policy = (
            policy
            or ToolPolicy()
        )



    # ======================================================
    # Properties
    # ======================================================


    @property
    def policy(
        self,
    ) -> ToolPolicy:

        return self._policy



    # ======================================================
    # Execute
    # ======================================================


    def execute(
        self,
        tool,
        **kwargs: Any,
    ) -> Any:
        """
        Execute tool safely.

        Supports:

        1. Tool object

            tool.run(...)

        2. Callable

            lambda: value
        """



        # --------------------------------------------------
        # Resolve name
        # --------------------------------------------------


        tool_name = getattr(
            tool,
            "name",
            tool.__class__.__name__,
        )



        # --------------------------------------------------
        # Policy
        # --------------------------------------------------


        if not self._policy.validate(
            tool_name
        ):

            return ToolResult.fail(
                PermissionError(
                    f"Tool blocked: {tool_name}"
                )
            )



        self._policy.record_call()



        # --------------------------------------------------
        # Normalize executor
        # --------------------------------------------------


        def runner():

            if hasattr(
                tool,
                "run",
            ):

                return tool.run(
                    **kwargs
                )


            if hasattr(
                tool,
                "execute",
            ):

                return tool.execute(
                    **kwargs
                )


            if callable(tool):

                return tool(
                    **kwargs
                )


            raise TypeError(
                "Tool must be callable or implement run()"
            )



        # --------------------------------------------------
        # Execute isolated
        # --------------------------------------------------


        timeout = (
            self._policy.timeout_seconds
        )


        try:

            with ThreadPoolExecutor(
                max_workers=1
            ) as executor:


                future = executor.submit(
                    runner
                )


                result = future.result(
                    timeout=timeout
                )



            if isinstance(
                result,
                ToolResult,
            ):

                return result



            # Compatibility:
            # plain callable returns raw value

            if (
                callable(tool)
                and
                not hasattr(tool, "run")
                and
                not hasattr(tool, "execute")
            ):

                return result



            return ToolResult.ok(
                result
            )



        except FutureTimeoutError:


            return ToolResult.fail(
                TimeoutError(
                    f"Tool timeout: {tool_name}"
                )
            )



        except Exception as exc:


            return ToolResult.fail(
                exc
            )



    # ======================================================
    # Batch Execute
    # ======================================================


    def execute_many(
        self,
        tool,
        inputs: list[dict[str, Any]],
    ) -> list[ToolResult]:
        """
        Execute multiple calls.
        """


        results = []


        for params in inputs:

            results.append(
                self.execute(
                    tool,
                    **params,
                )
            )


        return results



    # ======================================================
    # Diagnostics
    # ======================================================


    def status(
        self,
    ) -> dict[str, Any]:


        return {

            "policy":
                self._policy.to_dict(),

        }



    # ======================================================
    # Protocol
    # ======================================================


    def __repr__(
        self,
    ) -> str:


        return (
            "ToolSandbox("
            f"timeout={self._policy.timeout_seconds}"
            ")"
        )
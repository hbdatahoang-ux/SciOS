"""
SciOS Reflection Evaluator
==========================

Evaluates execution results.

Compatible APIs:
- evaluate()
- process()

Python 3.11+
"""

from __future__ import annotations

from typing import Any


__all__ = [
    "Evaluator",
]


class Evaluator:
    """
    Evaluator component of reflection pipeline.
    """


    def __init__(self) -> None:

        self.count = 0


    # ======================================================
    # Core API
    # ======================================================

    def evaluate(
        self,
        execution_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Evaluate execution result.

        Input:

        {
            "success": True,
            "output": "..."
        }

        """

        self.count += 1


        success = bool(
            execution_result.get(
                "success",
                False,
            )
        )


        result: dict[str, Any] = {

            "success":
                success,


            "output":
                execution_result.get(
                    "output"
                ),


            "error":
                execution_result.get(
                    "error"
                ),


            "evaluated":
                True,

        }


        if success:

            result["status"] = (
                "success"
            )

            result["message"] = (
                "Execution succeeded"
            )


        else:

            result["status"] = (
                "failed"
            )

            result["message"] = (
                "Execution failed"
            )


        return result


    # ======================================================
    # Process API
    # ======================================================

    def process(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generic evaluator entrypoint.

        Accepts:

        {
            "execution_result": {
                "success": True
            }
        }

        """

        execution_result = data.get(
            "execution_result",
            data,
        )


        return self.evaluate(
            execution_result
        )


    # ======================================================
    # Status
    # ======================================================

    def status(
        self,
    ) -> dict[str, Any]:

        return {

            "count":
                self.count,

        }


    # ======================================================
    # Reset
    # ======================================================

    def reset(
        self,
    ) -> None:

        self.count = 0


    # ======================================================
    # Protocol
    # ======================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}"
            f"(count={self.count})"

        )
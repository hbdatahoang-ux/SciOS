"""
SciOS Tool Recovery
===================

Robust recovery controller for tool execution.

Responsibilities
----------------
- Execute tool with retry policy
- Track execution attempts
- Capture failures
- Support fallback execution
- Reset lifecycle state
- Export diagnostics
- Provide stable public API

Python 3.11+
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional


__all__ = [
    "Recovery",
]


class Recovery:
    """
    Recovery manager for failed tool execution.

    Example
    -------
    >>> recovery = Recovery(max_retries=3)
    >>> recovery.run(callable_task)
    """

    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        max_retries: int = 1,
    ) -> None:

        if max_retries < 1:
            raise ValueError(
                "max_retries must be >= 1"
            )

        self.max_retries = max_retries

        self.attempts: int = 0

        self.status: str = "idle"

        self.message: Optional[str] = None

        self.errors: list[str] = []

        self.history: list[dict[str, Any]] = []


    # ==========================================================
    # Execution
    # ==========================================================

    def run(
        self,
        func: Callable[[], Any],
        fallback: Callable[[], Any] | None = None,
    ) -> Any:
        """
        Execute function with retry and fallback.

        Retry semantics:
        ----------------
        attempts counts completed attempts.

        Example:
            First call fails  -> attempts = 1
            Second call works -> attempts = 2

        This keeps compatibility with SciOS tests.
        """

        self.reset()

        last_error: Exception | None = None


        for attempt in range(
            1,
            self.max_retries + 1,
        ):

            try:

                result = func()


                self.attempts = attempt

                self.status = (
                    "success"
                )

                self.history.append(
                    {
                        "attempt": attempt,
                        "status": "success",
                    }
                )

                return result


            except Exception as exc:

                last_error = exc

                self.attempts = attempt

                self.status = (
                    "error"
                )

                self.message = str(
                    exc
                )

                self.errors.append(
                    str(exc)
                )


                self.history.append(
                    {
                        "attempt": attempt,
                        "status": "error",
                        "error": str(exc),
                    }
                )


        # ==================================================
        # Fallback
        # ==================================================

        if fallback is not None:

            try:

                result = fallback()

                self.status = (
                    "fallback"
                )

                self.history.append(
                    {
                        "status": "fallback",
                    }
                )

                return result


            except Exception as exc:

                self.status = (
                    "failed"
                )

                self.message = str(
                    exc
                )

                self.errors.append(
                    str(exc)
                )


        raise RuntimeError(
            self.message
            or (
                str(last_error)
                if last_error
                else "Recovery failed"
            )
        )


    # ==========================================================
    # Lifecycle
    # ==========================================================

    def reset(
        self,
    ) -> None:
        """
        Reset current recovery state.
        """

        self.attempts = 0

        self.status = (
            "idle"
        )

        self.message = None

        self.errors.clear()

        self.history.clear()


    # ==========================================================
    # Diagnostics
    # ==========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Export recovery state.
        """

        return {
            "max_retries": self.max_retries,
            "attempts": self.attempts,
            "status": self.status,
            "message": self.message,
            "errors": list(
                self.errors
            ),
            "history": list(
                self.history
            ),
        }


    def report(
        self,
    ) -> Dict[str, Any]:
        """
        Alias for diagnostics.
        """

        return self.to_dict()


    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __bool__(
        self,
    ) -> bool:
        """
        Recovery succeeded.
        """

        return self.status == "success"


    def __len__(
        self,
    ) -> int:
        """
        Number of execution attempts.
        """

        return self.attempts


    def __repr__(
        self,
    ) -> str:

        return (
            f"<{self.__class__.__name__} "
            f"status={self.status} "
            f"attempts={self.attempts}>"
        )
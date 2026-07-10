"""
SciOS Runtime Worker
====================

Worker abstraction for the SciOS Runtime.

Responsibilities
----------------
- Execute a single runtime work cycle.
- Delegate execution to RuntimeExecutor.
- Maintain worker execution statistics.

The Worker intentionally does NOT:
- own a Scheduler
- know about the Kernel
- know about the Cognitive Pipeline
- implement execution logic
"""

from __future__ import annotations

from typing import Any

from .executor import RuntimeExecutor

__all__ = [
    "Worker",
]


class Worker:
    """
    Runtime worker.

    A Worker is responsible for executing one work cycle by
    delegating to the RuntimeExecutor.

    Runtime
        ↓
    RuntimeLoop
        ↓
    Worker
        ↓
    RuntimeExecutor
    """

    def __init__(self, executor: RuntimeExecutor) -> None:

        self._executor = executor

        self._cycles = 0
        self._executed = 0

    # ==========================================================
    # Execution
    # ==========================================================

    def work(self) -> Any:
        """
        Execute one work cycle.

        Returns
        -------
        Any | None
            Result returned by the RuntimeExecutor.
        """

        self._cycles += 1

        result = self._executor.execute()

        if result is not None:
            self._executed += 1

        return result

    def tick(self) -> Any:
        """
        Alias for work().

        Allows RuntimeLoop to remain implementation-agnostic.
        """

        return self.work()

    # ==========================================================
    # Utilities
    # ==========================================================

    def reset(self) -> None:
        """
        Reset worker statistics.
        """

        self._cycles = 0
        self._executed = 0

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def executor(self) -> RuntimeExecutor:
        return self._executor

    @property
    def cycles(self) -> int:
        return self._cycles

    @property
    def executed(self) -> int:
        return self._executed

    # ==========================================================
    # Status
    # ==========================================================

    def status(self) -> dict[str, Any]:
        """
        Return worker status.
        """

        return {
            "cycles": self._cycles,
            "executed": self._executed,
        }

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __repr__(self) -> str:
        return (
            "Worker("
            f"cycles={self._cycles}, "
            f"executed={self._executed})"
        )
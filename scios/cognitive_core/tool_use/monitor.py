"""
SciOS Tool Monitor
==================

Execution monitoring for Tool Use.

Features
--------
- Track task lifecycle.
- Measure duration.
- Store execution history.
- FIFO ordering.
- Error tracking.
- Snapshot export.
- Reset lifecycle.

Python 3.11+
"""

from __future__ import annotations


from time import perf_counter

from typing import Any


__all__ = [
    "Monitor",
]



class Monitor:
    """
    Tool execution monitor.

    Lifecycle:

        start()
            |
            v
        end()
            |
            v
        entries[]
    """



    def __init__(
        self,
    ) -> None:

        # Public compatibility API
        self.entries: list[
            dict[str, Any]
        ] = []


        # Internal active tasks

        self._active: dict[
            str,
            float,
        ] = {}



    # ======================================================
    # Lifecycle
    # ======================================================


    def start(
        self,
        task: str,
    ) -> None:
        """
        Start monitoring task.
        """

        self._active[task] = perf_counter()



    def end(
        self,
        task: str,
        *,
        status: str = "success",
        message: str | None = None,
    ) -> dict[str, Any]:
        """
        Finish monitoring task.
        """

        start_time = self._active.pop(
            task,
            None,
        )


        if start_time is None:

            duration = 0.0

        else:

            duration = (
                perf_counter()
                -
                start_time
            )



        entry: dict[str, Any] = {

            "task": task,

            "status": status,

            "duration": duration,

        }


        if message is not None:

            entry["message"] = message



        self.entries.append(
            entry
        )


        return entry



    # ======================================================
    # Query
    # ======================================================


    def latest(
        self,
    ) -> dict[str, Any] | None:
        """
        Return latest entry.
        """

        if not self.entries:

            return None


        return self.entries[-1]



    def count(
        self,
    ) -> int:
        """
        Number of completed tasks.
        """

        return len(
            self.entries
        )



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Export monitor state.
        """

        return {

            "entries":
                list(self.entries)

        }



    snapshot = to_dict



    # ======================================================
    # Maintenance
    # ======================================================


    def clear(
        self,
    ) -> None:
        """
        Clear history.
        """

        self.entries.clear()

        self._active.clear()



    reset = clear



    # ======================================================
    # Protocols
    # ======================================================


    def __len__(
        self,
    ) -> int:

        return len(
            self.entries
        )



    def __bool__(
        self,
    ) -> bool:

        return bool(
            self.entries
        )



    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"entries={len(self.entries)}"

            ")"

        )
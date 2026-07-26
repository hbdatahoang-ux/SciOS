"""
SciOS-NG Timer Metric
=====================

Timer metric for measuring execution duration.

Responsibilities
-----------------
- Start timing.
- Stop timing.
- Measure elapsed duration.
- Record multiple durations.
- Provide statistics.
- Support context manager usage.

Python 3.11+
"""

from __future__ import annotations


import time

from contextlib import contextmanager
from copy import deepcopy
from typing import Any, Iterator


from .histogram import Histogram



__all__ = [
    "Timer",
]



# ==========================================================
# Timer Metric
# ==========================================================


class Timer(Histogram):
    """
    Timer metric.

    Timer extends Histogram to collect
    duration measurements.

    Example
    -------

        timer = Timer(
            name="task_latency"
        )

        timer.start()

        do_work()

        timer.stop()


    Context usage:

        with timer:

            do_work()

    """



    def __init__(
        self,
        name: str,
        **kwargs: Any,
    ):

        super().__init__(
            name=name,
            **kwargs,
        )


        self._started_at: float | None = None



    # ======================================================
    # Timing API
    # ======================================================


    def start(
        self,
    ) -> float:
        """
        Start timer.
        """

        self._started_at = time.perf_counter()


        return self._started_at



    def stop(
        self,
    ) -> float:
        """
        Stop timer and record duration.
        """

        if self._started_at is None:

            return 0.0



        elapsed = (
            time.perf_counter()
            -
            self._started_at
        )


        self._started_at = None


        self.observe(
            elapsed
        )


        return elapsed



    def elapsed(
        self,
    ) -> float:
        """
        Current elapsed duration.
        """

        if self._started_at is None:

            return 0.0



        return (
            time.perf_counter()
            -
            self._started_at
        )



    # ======================================================
    # Context Manager
    # ======================================================


    def __enter__(
        self,
    ) -> "Timer":

        self.start()

        return self



    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> None:

        self.stop()



    @contextmanager
    def measure(
        self,
    ) -> Iterator[None]:
        """
        Context helper.

        Example:

            with timer.measure():

                work()

        """

        self.start()


        try:

            yield


        finally:

            self.stop()



    # ======================================================
    # Runtime API
    # ======================================================


    @property
    def running(
        self,
    ) -> bool:
        """
        Whether timer is active.
        """

        return (
            self._started_at is not None
        )



    # ======================================================
    # Lifecycle
    # ======================================================


    def reset(
        self,
    ) -> None:
        """
        Reset timer.
        """

        super().reset()


        self._started_at = None



    # ======================================================
    # Snapshot
    # ======================================================


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Export timer state.
        """

        data = super().snapshot()


        data.update(
            {

                "running":
                    self.running,


                "elapsed":
                    self.elapsed(),

            }
        )


        return data



    # ======================================================
    # Serialization
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:

        data = self.snapshot()


        data["type"] = "timer"


        return data



    # ======================================================
    # Copy
    # ======================================================


    def copy(
        self,
    ) -> "Timer":

        return deepcopy(
            self
        )
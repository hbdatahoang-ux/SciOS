"""
SciOS Timing Utilities
======================

Performance measurement utilities used throughout the
Scientific Cognitive Operating System (SciOS).

Features
--------
- High-resolution timer
- Context manager
- Function decorator
- Execution statistics
- Named measurements
"""

from __future__ import annotations

import functools
import time
from dataclasses import dataclass
from typing import Any
from typing import Callable

__all__ = [
    "Timer",
    "TimerResult",
    "timed",
    "measure",
]


# ==========================================================
# Timer Result
# ==========================================================


@dataclass(slots=True)
class TimerResult:
    """
    Result of a timing measurement.
    """

    name: str
    start: float
    end: float
    elapsed: float

    @property
    def milliseconds(self) -> float:
        return self.elapsed * 1000

    @property
    def microseconds(self) -> float:
        return self.elapsed * 1_000_000

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "start": self.start,
            "end": self.end,
            "elapsed": self.elapsed,
            "milliseconds": self.milliseconds,
            "microseconds": self.microseconds,
        }

    def __str__(self) -> str:
        return (
            f"{self.name}: "
            f"{self.milliseconds:.3f} ms"
        )


# ==========================================================
# Timer
# ==========================================================


class Timer:
    """
    High-resolution timer.

    Examples
    --------

    >>> with Timer("kernel_boot") as t:
    ...     kernel.boot()

    >>> print(t.result.elapsed)
    """

    def __init__(
        self,
        name: str = "timer",
    ):
        self.name = name

        self._start = 0.0
        self._end = 0.0

        self.result: TimerResult | None = None

    # ------------------------------------------------------

    def start(self) -> None:
        self._start = time.perf_counter()

    # ------------------------------------------------------

    def stop(self) -> TimerResult:

        self._end = time.perf_counter()

        self.result = TimerResult(
            name=self.name,
            start=self._start,
            end=self._end,
            elapsed=self._end - self._start,
        )

        return self.result

    # ------------------------------------------------------

    @property
    def elapsed(self) -> float:

        if self.result is None:
            return 0.0

        return self.result.elapsed

    # ------------------------------------------------------

    def __enter__(self):

        self.start()

        return self

    # ------------------------------------------------------

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ):

        self.stop()


# ==========================================================
# Decorator
# ==========================================================


def timed(
    func: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Measure execution time of a function.

    Example
    -------

    >>> @timed
    ... def search():
    ...     ...

    """

    @functools.wraps(func)
    def wrapper(
        *args,
        **kwargs,
    ):

        timer = Timer(func.__qualname__)

        timer.start()

        result = func(
            *args,
            **kwargs,
        )

        measurement = timer.stop()

        print(
            f"[Timer] "
            f"{measurement}"
        )

        return result

    return wrapper


# ==========================================================
# Simple Measurement
# ==========================================================


def measure(
    func: Callable[..., Any],
    *args,
    **kwargs,
) -> TimerResult:
    """
    Execute a callable and return timing statistics.

    Example
    -------

    >>> result = measure(kernel.boot)
    >>> print(result.elapsed)
    """

    timer = Timer(func.__qualname__)

    timer.start()

    func(
        *args,
        **kwargs,
    )

    return timer.stop()
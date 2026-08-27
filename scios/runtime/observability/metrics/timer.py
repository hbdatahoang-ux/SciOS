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
- Support decorator usage.
- Provide snapshot/restore lifecycle.
- Provide thread-safe recording.

Python 3.11+
"""

from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from copy import deepcopy
from functools import wraps
from typing import Any, Callable, Iterator, TypeVar

from .histogram import Histogram


__all__ = [
    "Timer",
]


F = TypeVar("F", bound=Callable[..., Any])


# ==============================================================================
# Timer Metric
# ==============================================================================


class Timer(Histogram):
    """
    Timer metric.

    Timer extends ``Histogram`` to collect duration measurements while
    providing explicit timing, context-manager, and decorator APIs.

    Examples
    --------
    Explicit timing::

        timer = Timer("task_latency")

        timer.start()

        do_work()

        timer.stop()

    Direct recording::

        timer.record(0.125)

    Context usage::

        with timer:
            do_work()

    Decorator usage::

        @timer
        def do_work():
            ...
    """

    # ==========================================================================
    # Initialization
    # ==========================================================================

    def __init__(
        self,
        name: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            name=name,
            **kwargs,
        )

        self._started_at: float | None = None
        self._timer_lock = threading.RLock()

    # ==========================================================================
    # Public statistics API
    # ==========================================================================

    @property
    def sum(self) -> float:
        """
        Return the total recorded duration.

        ``Timer`` exposes this as a property because duration statistics are
        part of its public metric API.
        """
        with self._timer_lock:
            return self.total

    @property
    def average(self) -> float:
        """
        Return the average recorded duration.
        """
        with self._timer_lock:
            if not self._values:
                return 0.0

            return self.total / len(self._values)

    @property
    def minimum(self) -> float | None:
        """
        Return the minimum recorded duration.
        """
        with self._timer_lock:
            if not self._values:
                return None

            return min(self._values)

    @property
    def maximum(self) -> float | None:
        """
        Return the maximum recorded duration.
        """
        with self._timer_lock:
            if not self._values:
                return None

            return max(self._values)

    # ==========================================================================
    # Recording API
    # ==========================================================================

    def record(
        self,
        duration: int | float,
    ) -> float:
        """
        Record one duration.

        Parameters
        ----------
        duration:
            Duration in seconds.

        Returns
        -------
        float
            Normalized duration.

        Raises
        ------
        TypeError
            If ``duration`` cannot be converted to float.
        """
        normalized = float(duration)

        with self._timer_lock:
            self._values.append(normalized)
            self.touch()

        return normalized

    # ==========================================================================
    # Timing API
    # ==========================================================================

    def start(self) -> float:
        """
        Start the timer.

        Returns
        -------
        float
            The ``perf_counter()`` timestamp used as the start point.

        Raises
        ------
        RuntimeError
            If the timer is already running.
        """
        with self._timer_lock:
            if self._started_at is not None:
                raise RuntimeError(
                    "timer is already running"
                )

            self._started_at = time.perf_counter()

            return self._started_at

    def stop(self) -> float:
        """
        Stop the timer and record the elapsed duration.

        Returns
        -------
        float
            Elapsed duration in seconds.

        Raises
        ------
        RuntimeError
            If the timer is not running.
        """
        with self._timer_lock:
            if self._started_at is None:
                raise RuntimeError(
                    "timer is not running"
                )

            elapsed = (
                time.perf_counter()
                - self._started_at
            )

            self._started_at = None

            self.record(elapsed)

            return elapsed

    def elapsed(self) -> float:
        """
        Return the current elapsed duration.

        Returns ``0.0`` when the timer is not running.
        """
        with self._timer_lock:
            if self._started_at is None:
                return 0.0

            return (
                time.perf_counter()
                - self._started_at
            )

    # ==========================================================================
    # Runtime API
    # ==========================================================================

    @property
    def running(self) -> bool:
        """
        Return whether the timer is currently running.
        """
        with self._timer_lock:
            return self._started_at is not None

    # ==========================================================================
    # Context Manager
    # ==========================================================================

    def __enter__(self) -> "Timer":
        """
        Start timing when entering a context.
        """
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: Any,
    ) -> None:
        """
        Stop timing when leaving a context.
        """
        self.stop()

    @contextmanager
    def measure(self) -> Iterator[None]:
        """
        Measure a block of code.

        Example::

            with timer.measure():
                work()
        """
        self.start()

        try:
            yield
        finally:
            self.stop()

    # ==========================================================================
    # Decorator
    # ==========================================================================

    def __call__(
        self,
        function: F,
    ) -> F:
        """
        Use the timer as a function decorator.

        The wrapped function is timed and the duration is recorded whether
        the function returns normally or raises an exception.
        """

        if not callable(function):
            raise TypeError(
                "Timer can only decorate callable objects"
            )

        @wraps(function)
        def wrapper(
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            self.start()

            try:
                return function(
                    *args,
                    **kwargs,
                )
            finally:
                self.stop()

        return wrapper  # type: ignore[return-value]

    # ==========================================================================
    # Lifecycle
    # ==========================================================================

    def reset(self) -> None:
        """
        Reset all recorded durations and stop the timer.
        """
        with self._timer_lock:
            self._values.clear()
            self._started_at = None
            self.touch()

    # ==========================================================================
    # Snapshot
    # ==========================================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Export timer state.
        """
        with self._timer_lock:
            return {
                "name": self.name,
                "type": "timer",
                "values": list(self._values),
                "count": len(self._values),
                "sum": float(sum(self._values)),
                "average": (
                    float(sum(self._values) / len(self._values))
                    if self._values
                    else 0.0
                ),
                "min": (
                    min(self._values)
                    if self._values
                    else None
                ),
                "max": (
                    max(self._values)
                    if self._values
                    else None
                ),
                "labels": dict(self.labels),
                "running": self._started_at is not None,
                "elapsed": (
                    time.perf_counter() - self._started_at
                    if self._started_at is not None
                    else 0.0
                ),
            }

    # ==========================================================================
    # Restore
    # ==========================================================================

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> "Timer":
        """
        Restore recorded duration values from a snapshot.

        The restored timer is left stopped. Historical measurements are
        restored, but an active timing interval is never resumed.
        """
        if not isinstance(snapshot, dict):
            raise TypeError(
                "snapshot must be a dictionary"
            )

        values = snapshot.get(
            "values",
            [],
        )

        if not isinstance(values, list):
            raise TypeError(
                "snapshot 'values' must be a list"
            )

        normalized: list[float] = []

        for value in values:
            normalized.append(
                float(value)
            )

        with self._timer_lock:
            self._values = normalized
            self._started_at = None
            self.touch()

        return self

    # ==========================================================================
    # Serialization
    # ==========================================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize timer state.
        """
        return self.snapshot()

    # ==========================================================================
    # Copy
    # ==========================================================================

    def copy(self) -> "Timer":
        """
        Create an independent timer copy.
        """
        with self._timer_lock:
            copied = Timer(
                name=self.name,
                description=getattr(
                    self,
                    "description",
                    None,
                ),
                unit=getattr(
                    self,
                    "unit",
                    None,
                ),
                labels=dict(self.labels),
            )

            copied._values = list(
                self._values
            )

            copied._started_at = None

            return copied

    # ==========================================================================
    # Numeric Protocol
    # ==========================================================================

    def __float__(self) -> float:
        """
        Return the total recorded duration.
        """
        return self.sum

    # ==========================================================================
    # Representation
    # ==========================================================================

    def __repr__(self) -> str:
        """
        Return a Timer-specific representation.
        """
        return (
            "Timer("
            f"name={self.name!r}, "
            f"count={self.count}, "
            f"sum={self.sum}, "
            f"labels={self.labels!r}"
            ")"
        )
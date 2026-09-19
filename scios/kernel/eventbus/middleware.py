"""
SciOS Event Middleware
======================

Middleware pipeline for the SciOS Kernel EventBus.

Responsibilities
----------------
- Event preprocessing
- Event postprocessing
- Logging
- Tracing
- Metrics
- Timing
- Exception isolation

Design Goals
------------
- Composable
- Thread-safe
- Lightweight
- Open/Closed Principle
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from datetime import datetime
from datetime import timezone
from time import perf_counter
from typing import Any

from .event import Event

__all__ = [
    "EventMiddleware",
    "MiddlewarePipeline",
    "LoggingMiddleware",
    "TracingMiddleware",
    "MetricsMiddleware",
]


# ==========================================================
# Base Middleware
# ==========================================================


class EventMiddleware(ABC):
    """
    Base class for EventBus middleware.

    Middleware receives an Event and returns
    the (possibly modified) Event.
    """

    @abstractmethod
    def process(
        self,
        event: Event,
    ) -> Event:
        """
        Process an event.
        """

    def __call__(
        self,
        event: Event,
    ) -> Event:
        return self.process(event)


# ==========================================================
# Middleware Pipeline
# ==========================================================


class MiddlewarePipeline:
    """
    Sequential middleware execution.
    """

    def __init__(self) -> None:

        self._middleware: list[EventMiddleware] = []

    def add(
        self,
        middleware: EventMiddleware,
    ) -> None:

        self._middleware.append(middleware)

    def remove(
        self,
        middleware: EventMiddleware,
    ) -> None:

        if middleware in self._middleware:
            self._middleware.remove(middleware)

    def clear(self) -> None:
        self._middleware.clear()

    def process(
        self,
        event: Event,
    ) -> Event:

        current = event

        for middleware in self._middleware:

            try:
                current = middleware(current)

            except Exception:
                # Never stop event propagation.
                continue

        return current

    def __call__(
        self,
        event: Event,
    ) -> Event:
        return self.process(event)

    def __len__(self) -> int:
        return len(self._middleware)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(middleware={len(self)})"
        )


# ==========================================================
# Logging Middleware
# ==========================================================


class LoggingMiddleware(EventMiddleware):
    """
    Simple in-memory logging middleware.
    """

    def __init__(self) -> None:

        self.logs: list[dict[str, Any]] = []

    def process(
        self,
        event: Event,
    ) -> Event:

        self.logs.append(
            {
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
                "topic": event.topic,
                "event_id": event.event_id,
            }
        )

        return event

    def clear(self) -> None:
        self.logs.clear()

    @property
    def count(self) -> int:
        return len(self.logs)


# ==========================================================
# Tracing Middleware
# ==========================================================


class TracingMiddleware(EventMiddleware):
    """
    Adds tracing metadata to events.
    """

    def process(
        self,
        event: Event,
    ) -> Event:

        payload = dict(event.payload)

        payload.setdefault(
            "trace_timestamp",
            datetime.now(
                timezone.utc
            ).isoformat(),
        )

        return event.copy(payload=payload)


# ==========================================================
# Metrics Middleware
# ==========================================================


class MetricsMiddleware(EventMiddleware):
    """
    Collect middleware metrics.
    """

    def __init__(self) -> None:

        self.events_processed = 0
        self.total_processing_time = 0.0

    def process(
        self,
        event: Event,
    ) -> Event:

        start = perf_counter()

        self.events_processed += 1

        elapsed = perf_counter() - start

        self.total_processing_time += elapsed

        return event

    @property
    def average_processing_time(self) -> float:

        if self.events_processed == 0:
            return 0.0

        return (
            self.total_processing_time
            / self.events_processed
        )

    def status(self) -> dict[str, Any]:

        return {
            "events_processed": self.events_processed,
            "total_processing_time": self.total_processing_time,
            "average_processing_time": self.average_processing_time,
        }

    def reset(self) -> None:

        self.events_processed = 0
        self.total_processing_time = 0.0
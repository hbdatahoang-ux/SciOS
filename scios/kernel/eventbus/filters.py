"""
SciOS Event Filters
===================

Filtering framework for the SciOS Kernel EventBus.

Responsibilities
----------------
- Accept or reject events
- Topic filtering
- Source filtering
- Predicate filtering
- Composite filters

Design Goals
------------
- Lightweight
- Composable
- Thread-safe
- Open/Closed Principle
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from fnmatch import fnmatch

from .event import Event

__all__ = [
    "EventFilter",
    "AllowAllFilter",
    "DenyAllFilter",
    "TopicFilter",
    "SourceFilter",
    "PredicateFilter",
    "CompositeFilter",
]


# ==========================================================
# Base Filter
# ==========================================================


class EventFilter(ABC):
    """
    Base class for all event filters.

    A filter returns True if the event should continue
    through the EventBus pipeline.
    """

    @abstractmethod
    def accepts(
        self,
        event: Event,
    ) -> bool:
        """
        Return True to allow the event.
        """

    def __call__(
        self,
        event: Event,
    ) -> bool:
        return self.accepts(event)


# ==========================================================
# Built-in Filters
# ==========================================================


class AllowAllFilter(EventFilter):
    """
    Accept every event.
    """

    def accepts(
        self,
        event: Event,
    ) -> bool:
        return True


class DenyAllFilter(EventFilter):
    """
    Reject every event.
    """

    def accepts(
        self,
        event: Event,
    ) -> bool:
        return False


# ==========================================================
# Topic Filter
# ==========================================================


class TopicFilter(EventFilter):
    """
    Filter events by topic.

    Examples
    --------
    TopicFilter("task.completed")

    TopicFilter("runtime.*")

    TopicFilter("kernel.*")
    """

    def __init__(
        self,
        pattern: str,
    ) -> None:

        self.pattern = pattern

    def accepts(
        self,
        event: Event,
    ) -> bool:

        return fnmatch(
            event.topic,
            self.pattern,
        )

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(pattern={self.pattern!r})"
        )


# ==========================================================
# Source Filter
# ==========================================================


class SourceFilter(EventFilter):
    """
    Filter by event source.
    """

    def __init__(
        self,
        source: str,
    ) -> None:

        self.source = source

    def accepts(
        self,
        event: Event,
    ) -> bool:

        return event.source == self.source

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(source={self.source!r})"
        )


# ==========================================================
# Predicate Filter
# ==========================================================


class PredicateFilter(EventFilter):
    """
    Wrap an arbitrary predicate.
    """

    def __init__(
        self,
        predicate: Callable[[Event], bool],
    ) -> None:

        self.predicate = predicate

    def accepts(
        self,
        event: Event,
    ) -> bool:

        return self.predicate(event)


# ==========================================================
# Composite Filter
# ==========================================================


class CompositeFilter(EventFilter):
    """
    Combine multiple filters.

    mode="all"
        Every filter must pass.

    mode="any"
        At least one filter must pass.
    """

    def __init__(
        self,
        *filters: EventFilter,
        mode: str = "all",
    ) -> None:

        if mode not in {"all", "any"}:
            raise ValueError(
                "mode must be 'all' or 'any'"
            )

        self.filters = list(filters)
        self.mode = mode

    def add(
        self,
        event_filter: EventFilter,
    ) -> None:

        self.filters.append(event_filter)

    def remove(
        self,
        event_filter: EventFilter,
    ) -> None:

        if event_filter in self.filters:
            self.filters.remove(event_filter)

    def clear(self) -> None:

        self.filters.clear()

    def accepts(
        self,
        event: Event,
    ) -> bool:

        if not self.filters:
            return True

        if self.mode == "all":
            return all(
                f(event)
                for f in self.filters
            )

        return any(
            f(event)
            for f in self.filters
        )

    def __len__(self) -> int:
        return len(self.filters)

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(filters={len(self)}, "
            f"mode={self.mode!r})"
        )
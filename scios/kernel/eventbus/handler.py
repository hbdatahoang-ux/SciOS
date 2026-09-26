"""
SciOS Event Handlers
====================

Base event handler interfaces and implementations for the SciOS
Kernel EventBus.

Responsibilities
----------------
- Common handler abstraction
- Functional handler adapter
- Composite handlers
- Conditional handlers
- Exception isolation

Design Goals
------------
- Lightweight
- Extensible
- Type-safe
- Thread-safe
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from typing import Any

from .event import Event

__all__ = [
    "EventHandler",
    "FunctionHandler",
    "CompositeHandler",
    "ConditionalHandler",
]


# ==========================================================
# Base Handler
# ==========================================================

class EventHandler(ABC):
    """
    Abstract base class for all event handlers.
    """

    @abstractmethod
    def handle(
        self,
        event: Event,
    ) -> None:
        """
        Handle an event.
        """
        raise NotImplementedError

    def can_handle(
        self,
        event: Event,
    ) -> bool:
        """
        Whether this handler accepts the event.

        Default:
            Accept all events.
        """
        return True

    def __call__(
        self,
        event: Event,
    ) -> None:
        """
        Callable interface.
        """

        if self.can_handle(event):
            self.handle(event)


# ==========================================================
# Function Adapter
# ==========================================================

class FunctionHandler(EventHandler):
    """
    Wrap a Python callable as an EventHandler.

    Example
    -------
    >>> def log(event):
    ...     print(event.topic)

    >>> handler = FunctionHandler(log)
    """

    def __init__(
        self,
        func: Callable[[Event], None],
    ) -> None:
        self._func = func

    def handle(
        self,
        event: Event,
    ) -> None:
        self._func(event)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"({self._func.__name__})"
        )


# ==========================================================
# Composite Handler
# ==========================================================

class CompositeHandler(EventHandler):
    """
    Dispatch an event to multiple handlers.
    """

    def __init__(
        self,
        *handlers: EventHandler,
    ) -> None:

        self._handlers: list[EventHandler] = list(handlers)

    def add(
        self,
        handler: EventHandler,
    ) -> None:
        self._handlers.append(handler)

    def remove(
        self,
        handler: EventHandler,
    ) -> None:

        if handler in self._handlers:
            self._handlers.remove(handler)

    def clear(self) -> None:
        self._handlers.clear()

    def handle(
        self,
        event: Event,
    ) -> None:

        for handler in list(self._handlers):

            try:
                handler(event)

            except Exception:
                # Never stop propagation because
                # one handler failed.
                continue

    def __len__(self) -> int:
        return len(self._handlers)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(handlers={len(self)})"
        )


# ==========================================================
# Conditional Handler
# ==========================================================

class ConditionalHandler(EventHandler):
    """
    Execute a handler only when a predicate matches.
    """

    def __init__(
        self,
        predicate: Callable[[Event], bool],
        handler: EventHandler,
    ) -> None:

        self._predicate = predicate
        self._handler = handler

    def can_handle(
        self,
        event: Event,
    ) -> bool:
        return self._predicate(event)

    def handle(
        self,
        event: Event,
    ) -> None:
        self._handler(event)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(handler={self._handler!r})"
        )
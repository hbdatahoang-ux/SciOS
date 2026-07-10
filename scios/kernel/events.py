"""
SciOS Event Bus
===============

Responsibilities
----------------
- Provide a simple publish/subscribe mechanism.
- Allow kernel subsystems to emit lifecycle and artifact events.
- Ensure thread-safety for concurrent subscribers.

Does NOT:
- Persist events.
- Guarantee delivery order beyond FIFO.
- Handle complex routing.
"""

from __future__ import annotations

import threading
from typing import Any, Callable, List


__all__ = ["EventBus"]


class EventBus:
    """
    Thread-safe event bus.
    """

    def __init__(self) -> None:
        self._subscribers: List[Callable[[str], None]] = []
        self._lock = threading.RLock()

    # ==========================================================
    # Subscription
    # ==========================================================

    def subscribe(self, handler: Callable[[str], None]) -> None:
        """
        Subscribe a handler to events.

        Handler signature:
            def handler(event: str, **payload) -> None
        """
        with self._lock:
            self._subscribers.append(handler)

    def unsubscribe(self, handler: Callable[[str], None]) -> None:
        """Remove a handler."""
        with self._lock:
            if handler in self._subscribers:
                self._subscribers.remove(handler)

    # ==========================================================
    # Publishing
    # ==========================================================

    def publish(self, event: str, **payload: Any) -> None:
        """Publish an event to all subscribers."""
        with self._lock:
            subscribers = list(self._subscribers)
        for handler in subscribers:
            try:
                handler(event, **payload)
            except Exception:
                # swallow exceptions to avoid breaking bus
                continue

    # ==========================================================
    # Pythonic helpers
    # ==========================================================

    def __len__(self) -> int:
        return len(self._subscribers)

    def __repr__(self) -> str:
        return f"EventBus(subscribers={len(self)})"

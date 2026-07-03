"""
SciOS Kernel EventBus
=====================

Public exports for the Kernel EventBus subsystem.

The EventBus provides a lightweight publish/subscribe
communication mechanism for decoupling Kernel components.

Public API
----------
EventBus
    Kernel publish/subscribe event bus.
"""

from .bus import EventBus

__all__ = [
    "EventBus",
]
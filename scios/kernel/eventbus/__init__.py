"""
SciOS Kernel EventBus
=====================

Event-driven messaging infrastructure for the SciOS Kernel.

This package provides:

- EventBus
- Event
- Publisher
- Subscriber
- EventHandler
- EventMiddleware
- EventFilter
- Event topics
"""

from __future__ import annotations

# ==========================================================
# Core
# ==========================================================

from .bus import EventBus

from .event import Event

# ==========================================================
# Interfaces
# ==========================================================

from .publisher import Publisher

from .subscriber import Subscriber

from .handler import EventHandler

from .middleware import EventMiddleware

from .filters import EventFilter

# ==========================================================
# Topics
# ==========================================================

from .topics import *

# ==========================================================
# Version
# ==========================================================

__version__ = "0.3.0-alpha"

# ==========================================================
# Public API
# ==========================================================

__all__ = [
    "EventBus",
    "Event",
    "Publisher",
    "Subscriber",
    "EventHandler",
    "EventMiddleware",
    "EventFilter",
]
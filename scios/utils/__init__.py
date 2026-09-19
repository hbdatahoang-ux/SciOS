"""
SciOS Utility Library
=====================

Common stateless utility functions shared across SciOS.

The utilities package contains lightweight helper modules used
throughout the Kernel, Agents, Runtime, Memory and Substrate.

Modules
-------
serialization
    Object serialization utilities.

validation
    Validation helpers.

timing
    Performance measurement utilities.
"""

from .serialization import (
    Serializer,
    load_json,
    save_json,
)

from .validation import (
    Validator,
    require,
    require_not_none,
)

from .timing import (
    Timer,
    TimerResult,
    timed,
)

__all__ = [

    # Serialization
    "Serializer",
    "load_json",
    "save_json",

    # Validation
    "Validator",
    "require",
    "require_not_none",

    # Timing
    "Timer",
    "TimerResult",
    "timed",
]

# ==============================================================================
# scios/runtime/observability/metrics/runtime/__init__.py
# ==============================================================================

"""
SciOS Runtime Metrics Runtime API
=================================

Public runtime execution components.

Exports:

- RuntimeScheduler
- RuntimePipeline
- Runtime constants
- Package version

Python 3.11+
"""

from __future__ import annotations


# ==============================================================================
# Version
# ==============================================================================

__version__ = "0.1.0"


# ==============================================================================
# Scheduler
# ==============================================================================

from .scheduler import (
    RuntimeScheduler,

    DEFAULT_NAME as SCHEDULER_DEFAULT_NAME,
    DEFAULT_ENABLED as SCHEDULER_DEFAULT_ENABLED,
    DEFAULT_RUNNING as SCHEDULER_DEFAULT_RUNNING,

    DEFAULT_INTERVAL,
    DEFAULT_MAX_TICKS,
)


# ==============================================================================
# Pipeline
# ==============================================================================

from .pipeline import (
    RuntimePipeline,

    DEFAULT_NAME as PIPELINE_DEFAULT_NAME,
    DEFAULT_ENABLED as PIPELINE_DEFAULT_ENABLED,
    DEFAULT_RUNNING as PIPELINE_DEFAULT_RUNNING,
)


# ==============================================================================
# Public Constants
# ==============================================================================

DEFAULT_NAME = SCHEDULER_DEFAULT_NAME

DEFAULT_ENABLED = SCHEDULER_DEFAULT_ENABLED

DEFAULT_RUNNING = SCHEDULER_DEFAULT_RUNNING


# ==============================================================================
# Public API
# ==============================================================================

__all__ = [

    # ------------------------------------------------------------------
    # Version
    # ------------------------------------------------------------------

    "__version__",


    # ------------------------------------------------------------------
    # Runtime Components
    # ------------------------------------------------------------------

    "RuntimeScheduler",

    "RuntimePipeline",


    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "DEFAULT_NAME",

    "DEFAULT_ENABLED",

    "DEFAULT_RUNNING",

    "DEFAULT_INTERVAL",

    "DEFAULT_MAX_TICKS",

]
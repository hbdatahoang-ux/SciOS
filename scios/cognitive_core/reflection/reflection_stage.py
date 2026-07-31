"""
SciOS Reflection Stage Compatibility Module
===========================================

Backward compatibility export.

The canonical implementation lives in:

    scios.cognitive_core.reflection.stage
"""

from __future__ import annotations


from .stage import (
    ReflectionStage,
    StageTracker,
)


__all__ = [
    "ReflectionStage",
    "StageTracker",
]
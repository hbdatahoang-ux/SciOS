"""
SciOS Reasoning Subsystem
=========================

Unified cognitive reasoning subsystem for SciOS.

This package provides the public reasoning API used by the
Kernel, Runtime, and Agent Executor.

Modules
-------
- engine       : Unified reasoning engine
- state        : Runtime reasoning state
- planner      : Planning strategies
- inference    : Inference pipeline
- hypothesis   : Hypothesis generation
- verifier     : Result verification

Design
------
The reasoning subsystem exposes stable interfaces while allowing
different reasoning implementations (e.g. QTC, symbolic, neural,
hybrid) to evolve independently.
"""

from .engine import ReasoningEngine
from .state import ReasoningState

__all__ = (
    "ReasoningEngine",
    "ReasoningState",
)

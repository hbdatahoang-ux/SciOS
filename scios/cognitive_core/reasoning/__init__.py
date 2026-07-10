"""
SciOS Reasoning Package
=======================

Provides unified reasoning components for the SciOS cognitive core.

Public API
----------
- ReasoningEngine : Facade for reasoning pipeline
- ReasoningState  : Tracks queries and results
- ReasoningPlanner: Generates execution plans
- InferenceEngine : Performs logical inference
- HypothesisGenerator : Produces candidate hypotheses
- ReasoningVerifier : Validates hypotheses
- RuleEngine      : Rule-based reasoning utilities
- ProblemSolver   : General problem-solving utilities
- ReasoningStage  : Pipeline stage integration
"""

from __future__ import annotations

# Core facade and modules
from .engine import ReasoningEngine
from .state import ReasoningState
from .planner import ReasoningPlanner
from .inference import InferenceEngine
from .hypothesis import HypothesisGenerator
from .verifier import ReasoningVerifier

# Utilities
from .rules import RuleEngine
from .solver import ProblemSolver

# Pipeline stage
from .stage import ReasoningStage


__all__ = [
    "ReasoningEngine",
    "ReasoningState",
    "ReasoningPlanner",
    "InferenceEngine",
    "HypothesisGenerator",
    "ReasoningVerifier",
    "RuleEngine",
    "ProblemSolver",
    "ReasoningStage",
]

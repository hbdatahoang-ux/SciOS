"""
SciOS Reflection

Self-evaluation and critique subsystem.

Responsibilities
----------------
- Evaluate reasoning results
- Detect failures
- Score responses
- Generate feedback
"""

from .critic import Critic
from .evaluator import Evaluator

__all__ = [
    "Critic",
    "Evaluator",
]

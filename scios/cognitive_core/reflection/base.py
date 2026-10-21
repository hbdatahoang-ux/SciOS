# scios/cognitive_core/reflection/base.py

"""
SciOS Reflection Base
=====================

Defines abstract interfaces for reflection components.
All reflection modules (Evaluator, Critic, Analyzer, etc.)
should inherit from ReflectionComponent to ensure consistency.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict


class ReflectionComponent(ABC):
    """
    Abstract base class for all reflection components.
    Provides a standard interface for evaluation, analysis,
    feedback generation, and reporting.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return structured reflection output.
        Each subclass must implement its own logic.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<ReflectionComponent {self.name}>"

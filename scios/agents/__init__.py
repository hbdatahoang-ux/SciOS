"""
SciOS Agents
============

Public interface for the SciOS Cognitive Agent subsystem.

The Agents package provides the cognitive execution layer of
SciOS, including memory, reasoning, planning, tool use,
reflection, and multi-agent collaboration.

Public API
----------
BaseAgent
    Abstract base class for all cognitive agents.

AgentExecutor
    Cognitive execution orchestrator coordinating the
    reasoning pipeline.
"""

from .base import BaseAgent
from .executor import AgentExecutor

__all__ = [
    "BaseAgent",
    "AgentExecutor",
]

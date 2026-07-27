"""
SciOS Runtime Agent
===================

High level autonomous agent.

Python 3.11+
"""

from __future__ import annotations


from .state import AgentState
from .memory import Memory
from .planner import Planner


__all__ = [
    "Agent",
]



class Agent:
    """
    SciOS autonomous runtime agent.
    """



    def __init__(
        self,
        name: str,
    ) -> None:


        self.name = name

        self.state = AgentState()

        self.memory = Memory()

        self.planner = Planner()



    def run(
        self,
        task: str,
    ):


        self.state.update(
            status="running"
        )


        self.memory.add(
            task
        )


        plan = self.planner.plan(
            task
        )


        self.state.update(
            status="completed"
        )


        return plan



    def __repr__(self):

        return (
            "Agent("
            f"name={self.name!r}"
            ")"
        )
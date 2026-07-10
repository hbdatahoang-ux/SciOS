from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
from uuid import UUID, uuid4

from scios.cognitive_core.memory.semantic import SemanticMemory
from scios.cognitive_core.memory.episodic import EpisodicMemory
from scios.cognitive_core.memory.working import WorkingMemory


@dataclass
class ReasoningEngine:
    """
    ReasoningEngine = Performs logical inference using memory and rules.
    """

    engine_id: UUID = field(default_factory=uuid4)
    semantic: SemanticMemory = field(default_factory=SemanticMemory)
    episodic: EpisodicMemory = field(default_factory=EpisodicMemory)
    working: WorkingMemory = field(default_factory=WorkingMemory)
    rules: List[Dict[str, Any]] = field(default_factory=list)

    # =========================================================
    # Core API
    # =========================================================

    def add_rule(self, condition: str, conclusion: str) -> None:
        """
        Add a logical rule: IF condition THEN conclusion.
        """
        self.rules.append({"condition": condition, "conclusion": conclusion})

    def infer(self, context: Dict[str, Any]) -> List[str]:
        """
        Perform inference based on rules and context.
        """
        conclusions = []
        for rule in self.rules:
            if rule["condition"] in context.values():
                conclusions.append(rule["conclusion"])
        return conclusions

    def reason_about_goal(self, goal: Dict[str, Any]) -> List[str]:
        """
        Reason about a goal using semantic + episodic memory.
        """
        conclusions = []

        # Check semantic facts
        for key, value in self.semantic.all_facts().items():
            if key in goal.get("requirements", []):
                conclusions.append(f"Semantic match: {key} → {value}")

        # Check episodic experiences
        for ep in self.episodic.all_episodes():
            if goal.get("event") and goal["event"] in ep["event"]:
                conclusions.append(f"Episodic reference: {ep['event']} at {ep['timestamp']}")

        return conclusions

    # =========================================================
    # Utility
    # =========================================================

    def reset(self) -> None:
        """
        Reset reasoning engine state.
        """
        self.rules.clear()

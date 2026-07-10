"""
SciOS Rule Base
===============

Stores logical rules for inference.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
from uuid import UUID, uuid4


@dataclass
class RuleBase:
    """
    RuleBase = Stores logical rules for inference.
    """

    rulebase_id: UUID = field(default_factory=uuid4)
    rules: List[Dict[str, Any]] = field(
        default_factory=lambda: [
            {"condition": "rain", "conclusion": "carry umbrella"},
            {"condition": "hungry", "conclusion": "eat food"},
            {"condition": "tired", "conclusion": "take rest"},
            {"condition": "exam", "conclusion": "study hard"},
        ]
    )

    # =========================================================
    # Rule Management
    # =========================================================
    def add_rule(self, condition: str, conclusion: str) -> None:
        self.rules.append({"condition": condition, "conclusion": conclusion})

    def remove_rule(self, condition: str) -> None:
        self.rules = [r for r in self.rules if r["condition"] != condition]

    def get_rules(self) -> List[Dict[str, Any]]:
        return list(self.rules)

    def find_rules(self, keyword: str) -> List[Dict[str, Any]]:
        return [
            r for r in self.rules
            if keyword in r["condition"] or keyword in r["conclusion"]
        ]

    def clear(self) -> None:
        self.rules.clear()

    def status(self) -> Dict[str, Any]:
        return {"rules_count": len(self.rules)}

    def __repr__(self) -> str:
        return f"RuleBase(rules={len(self.rules)})"

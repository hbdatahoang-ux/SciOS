"""
SciOS Rule Engine
=================

Provides rule-based reasoning utilities built on RuleBase.
"""

from __future__ import annotations
from typing import Any, Dict, List
from .rulebase import RuleBase


class RuleEngine:
    """
    RuleEngine = Simple rule-based inference system.
    Wraps RuleBase and provides inference capability.
    """

    def __init__(self) -> None:
        self._rulebase = RuleBase()

    # =========================================================
    # Rule Management
    # =========================================================
    def add_rule(self, condition: str, conclusion: str) -> None:
        self._rulebase.add_rule(condition, conclusion)

    def remove_rule(self, condition: str) -> None:
        self._rulebase.remove_rule(condition)

    def get_rules(self) -> List[Dict[str, Any]]:
        return self._rulebase.get_rules()

    def clear(self) -> None:
        self._rulebase.clear()

    # =========================================================
    # Inference
    # =========================================================
    def infer(self, context: Dict[str, Any]) -> List[str]:
        """
        Perform inference: if a rule's condition matches any value in context,
        return its conclusion.
        """
        conclusions: List[str] = []
        for rule in self._rulebase.get_rules():
            if rule["condition"] in context.values():
                conclusions.append(rule["conclusion"])
        return conclusions

    # =========================================================
    # Utility
    # =========================================================
    def status(self) -> Dict[str, Any]:
        return {
            "rules_count": len(self._rulebase.get_rules()),
        }

    def __repr__(self) -> str:
        return f"RuleEngine(rules={len(self._rulebase.get_rules())})"

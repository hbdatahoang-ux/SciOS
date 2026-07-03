"""
SciOS Critic

Critiques reasoning results and identifies potential issues.
"""

from typing import Any, Dict, List


class Critic:
    """
    Reflection critic.

    Responsibilities
    ----------------
    - Inspect reasoning output
    - Detect inconsistencies
    - Produce improvement suggestions
    """

    def critique(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Critique a reasoning result.
        """

        issues: List[str] = []

        if not result:
            issues.append("Empty result.")

        if "reasoning" not in result:
            issues.append("Missing reasoning output.")

        if "response" not in result:
            issues.append("Missing final response.")

        return {
            "accepted": len(issues) == 0,
            "issues": issues,
            "suggestions": self._suggestions(issues),
        }

    def _suggestions(self, issues: List[str]) -> List[str]:
        """
        Generate improvement suggestions.
        """

        suggestions = []

        for issue in issues:

            if "reasoning" in issue.lower():
                suggestions.append(
                    "Invoke ReasoningEngine again."
                )

            elif "response" in issue.lower():
                suggestions.append(
                    "Generate a final response."
                )

            elif "empty" in issue.lower():
                suggestions.append(
                    "Re-execute the cognitive pipeline."
                )

        return suggestions

    def status(self) -> Dict[str, str]:
        """
        Return critic status.
        """

        return {
            "component": "Critic",
            "status": "ready",
        }
"""
SciOS Reasoning Verifier
========================

Verification component of the SciOS reasoning subsystem.

The verifier evaluates generated hypotheses and determines whether
they satisfy minimum consistency and confidence requirements before
they are returned by the ReasoningEngine.

Responsibilities
----------------
- Validate generated hypotheses
- Evaluate confidence
- Check evidence availability
- Produce structured verification results
- Remain independent of any reasoning backend
"""

from __future__ import annotations

from typing import Any


class ReasoningVerifier:
    """
    Verify generated reasoning hypotheses.
    """

    DEFAULT_THRESHOLD = 0.50

    def __init__(
        self,
        confidence_threshold: float = DEFAULT_THRESHOLD,
    ) -> None:
        self._threshold = confidence_threshold

    # ==========================================================
    # Public API
    # ==========================================================

    def verify(
        self,
        hypothesis: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Verify a generated hypothesis.
        """

        context = context or {}

        confidence = float(
            hypothesis.get("confidence", 0.0)
        )

        evidence = hypothesis.get("evidence", [])

        statement = hypothesis.get("statement", "")

        accepted = (
            confidence >= self._threshold
            and bool(statement)
            and len(evidence) > 0
        )

        issues = self._collect_issues(
            confidence,
            statement,
            evidence,
        )

        return {
            "accepted": accepted,
            "confidence": confidence,
            "threshold": self._threshold,
            "issues": issues,
            "context_size": len(context),
            "status": (
                "verified"
                if accepted
                else "rejected"
            ),
        }

    # ==========================================================
    # Internal helpers
    # ==========================================================

    def _collect_issues(
        self,
        confidence: float,
        statement: str,
        evidence: list[Any],
    ) -> list[str]:
        """
        Collect verification issues.
        """

        issues: list[str] = []

        if confidence < self._threshold:
            issues.append(
                "confidence below threshold"
            )

        if not statement:
            issues.append(
                "missing hypothesis statement"
            )

        if not evidence:
            issues.append(
                "no supporting evidence"
            )

        return issues

    # ==========================================================
    # Configuration
    # ==========================================================

    @property
    def confidence_threshold(self) -> float:
        """
        Return the minimum confidence threshold.
        """

        return self._threshold

    def set_threshold(
        self,
        value: float,
    ) -> None:
        """
        Update the confidence threshold.
        """

        if not (0.0 <= value <= 1.0):
            raise ValueError(
                "confidence threshold must be between 0.0 and 1.0"
            )

        self._threshold = value

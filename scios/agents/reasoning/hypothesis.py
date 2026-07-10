"""
SciOS Hypothesis Generator
==========================

Hypothesis generation component for the SciOS reasoning subsystem.

The hypothesis generator transforms intermediate inference results
into structured hypotheses that can later be evaluated by the
ReasoningVerifier.

Responsibilities
----------------
- Generate candidate hypotheses
- Assign confidence estimates
- Preserve supporting evidence
- Remain independent of reasoning backend
"""

from __future__ import annotations

from typing import Any


class HypothesisGenerator:
    """
    Generate reasoning hypotheses.

    This component converts intermediate inference results into
    structured candidate hypotheses.
    """

    def generate(
        self,
        query: str,
        inference: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate a hypothesis from inference results.
        """

        conclusions = inference.get("conclusions", [])
        evidence = inference.get("evidence", [])
        confidence = float(inference.get("confidence", 0.0))

        statement = self._build_statement(
            query=query,
            conclusions=conclusions,
        )

        hypothesis = {
            "id": 1,
            "query": query,
            "statement": statement,
            "confidence": confidence,
            "evidence": evidence,
            "conclusions": conclusions,
            "status": "generated",
        }

        return hypothesis

    # ==========================================================
    # Internal helpers
    # ==========================================================

    def _build_statement(
        self,
        query: str,
        conclusions: list[str],
    ) -> str:
        """
        Build a human-readable hypothesis statement.
        """

        if conclusions:
            return conclusions[0]

        return f"Hypothesis generated for: {query}"

    def rank(
        self,
        hypotheses: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Rank hypotheses by confidence.

        Highest-confidence hypotheses are returned first.
        """

        return sorted(
            hypotheses,
            key=lambda item: float(item.get("confidence", 0.0)),
            reverse=True,
        )

    def select_best(
        self,
        hypotheses: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        """
        Select the highest-ranked hypothesis.
        """

        ranked = self.rank(hypotheses)

        if not ranked:
            return None

        return ranked[0]

"""Deterministic natural-language interpretation of structured reasoning."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


class DeterministicNaturalLanguageReasoner:
    """Interpret deterministic evidence without changing or recomputing it."""

    def explain(
        self,
        *,
        query: str,
        evidence: Mapping[str, Any],
        reasoning: Sequence[Mapping[str, Any]],
    ) -> str:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string.")

        if not isinstance(evidence, Mapping):
            raise TypeError("evidence must be a mapping.")

        if not isinstance(reasoning, Sequence) or isinstance(
            reasoning, (str, bytes)
        ):
            raise TypeError("reasoning must be a sequence.")

        anomalies = self._collect_anomalies(reasoning)
        anomaly_count = len(anomalies)

        if anomaly_count == 0:
            return self._explain_no_anomalies(query, evidence)

        if anomaly_count == 1:
            return self._explain_single_anomaly(
                query,
                anomalies[0],
            )

        return self._explain_multiple_anomalies(
            query,
            anomalies,
        )

    @staticmethod
    def _collect_anomalies(
        reasoning: Sequence[Mapping[str, Any]],
    ) -> list[Mapping[str, Any]]:
        return [
            item
            for item in reasoning
            if item.get("is_outlier") is True
        ]

    @staticmethod
    def _explain_no_anomalies(
        query: str,
        evidence: Mapping[str, Any],
    ) -> str:
        rows = evidence.get("rows")
        columns = evidence.get("columns")

        if rows is not None and columns is not None:
            return (
                f"No anomalous numeric values were identified in the "
                f"dataset ({rows} rows, {columns} columns) using the "
                f"available deterministic evidence."
            )

        return (
            "No anomalous numeric values were identified using the "
            "available deterministic evidence."
        )

    @staticmethod
    def _explain_single_anomaly(
        query: str,
        reasoning: Mapping[str, Any],
    ) -> str:
        column = reasoning.get("column", "unknown column")
        index = reasoning.get("index", "unknown row")
        value = reasoning.get("value", "unknown value")
        evidence = reasoning.get("evidence", {})

        rule = evidence.get("rule", "the deterministic rule")
        upper_bound = evidence.get("upper_bound")
        lower_bound = evidence.get("lower_bound")

        if (
            upper_bound is not None
            and isinstance(value, (int, float))
            and value > upper_bound
        ):
            boundary = f"above the upper bound of {upper_bound}"
        elif (
            lower_bound is not None
            and isinstance(value, (int, float))
            and value < lower_bound
        ):
            boundary = f"below the lower bound of {lower_bound}"
        else:
            boundary = "outside the accepted range"

        explanation = (
            f"The value {value} in column '{column}' at row {index} "
            f"is classified as an outlier because it falls {boundary} "
            f"under the {rule} rule."
        )

        if _asks_about_cause(query):
            explanation += (
                " Possible explanations include a data-entry error, "
                "measurement error, a genuine rare event, or a change "
                "in the underlying distribution; the available "
                "evidence does not establish which cause is responsible."
            )

        return explanation

    @staticmethod
    def _explain_multiple_anomalies(
        query: str,
        anomalies: Sequence[Mapping[str, Any]],
    ) -> str:
        parts: list[str] = []

        for item in anomalies:
            column = item.get("column", "unknown column")
            index = item.get("index", "unknown row")
            value = item.get("value", "unknown value")
            evidence = item.get("evidence", {})
            rule = evidence.get("rule", "the deterministic rule")

            parts.append(
                f"{column}[row {index}]={value} "
                f"was classified as an outlier under the {rule} rule"
            )

        explanation = (
            f"{len(anomalies)} anomalous numeric value(s) were identified: "
            + "; ".join(parts)
            + "."
        )

        if _asks_about_cause(query):
            explanation += (
                " Possible explanations include data-entry or measurement "
                "errors, genuine rare events, or distribution shift; "
                "the available evidence does not establish a specific cause."
            )

        return explanation


def _asks_about_cause(query: str) -> bool:
    normalized = query.casefold()

    cause_terms = (
        "why",
        "cause",
        "caused",
        "reason",
        "explain",
        "error",
    )

    return any(term in normalized for term in cause_terms)

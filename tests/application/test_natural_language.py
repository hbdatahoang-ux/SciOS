from __future__ import annotations

from copy import deepcopy

from scios.application.natural_language import (
    DeterministicNaturalLanguageReasoner,
)


def make_evidence() -> dict[str, object]:
    return {
        "rows": 6,
        "columns": 1,
        "column_names": ["value"],
        "missing": {"value": 0},
        "outliers": {
            "value": {
                "count": 1,
                "indices": [5],
                "evidence": [
                    {
                        "column": "value",
                        "index": 5,
                        "value": 100.0,
                        "q1": 10.0,
                        "q3": 15.0,
                        "iqr": 5.0,
                        "lower_bound": 2.5,
                        "upper_bound": 22.5,
                        "rule": "IQR",
                    }
                ],
            }
        },
    }


def make_reasoning() -> list[dict[str, object]]:
    return [
        {
            "column": "value",
            "index": 5,
            "value": 100.0,
            "is_outlier": True,
            "evidence": {
                "column": "value",
                "index": 5,
                "value": 100.0,
                "q1": 10.0,
                "q3": 15.0,
                "iqr": 5.0,
                "lower_bound": 2.5,
                "upper_bound": 22.5,
                "rule": "IQR",
            },
        }
    ]


def test_explains_single_deterministic_outlier() -> None:
    reasoner = DeterministicNaturalLanguageReasoner()

    explanation = reasoner.explain(
        query="Why is this value anomalous?",
        evidence=make_evidence(),
        reasoning=make_reasoning(),
    )

    assert "100.0" in explanation
    assert "value" in explanation
    assert "row 5" in explanation
    assert "upper bound of 22.5" in explanation
    assert "IQR" in explanation


def test_cause_question_uses_hypothesis_language() -> None:
    reasoner = DeterministicNaturalLanguageReasoner()

    explanation = reasoner.explain(
        query="Could this be a data-entry error?",
        evidence=make_evidence(),
        reasoning=make_reasoning(),
    )

    assert "Possible explanations include" in explanation
    assert "does not establish which cause is responsible" in explanation


def test_no_anomaly_produces_valid_explanation() -> None:
    reasoner = DeterministicNaturalLanguageReasoner()

    evidence = {
        "rows": 10,
        "columns": 4,
    }

    explanation = reasoner.explain(
        query="Are there any anomalous values?",
        evidence=evidence,
        reasoning=[],
    )

    assert "No anomalous numeric values were identified" in explanation
    assert "10 rows" in explanation
    assert "4 columns" in explanation


def test_multiple_anomalies_are_all_interpreted() -> None:
    reasoner = DeterministicNaturalLanguageReasoner()

    reasoning = [
        {
            "column": "income",
            "index": 6,
            "value": 41000.0,
            "is_outlier": True,
            "evidence": {
                "rule": "IQR",
            },
        },
        {
            "column": "transaction_amount",
            "index": 9,
            "value": 12000.0,
            "is_outlier": True,
            "evidence": {
                "rule": "IQR",
            },
        },
    ]

    explanation = reasoner.explain(
        query="Which values are anomalous?",
        evidence={},
        reasoning=reasoning,
    )

    assert "2 anomalous numeric value(s)" in explanation
    assert "income[row 6]=41000.0" in explanation
    assert "transaction_amount[row 9]=12000.0" in explanation


def test_inputs_are_not_mutated() -> None:
    reasoner = DeterministicNaturalLanguageReasoner()

    evidence = make_evidence()
    reasoning = make_reasoning()

    evidence_before = deepcopy(evidence)
    reasoning_before = deepcopy(reasoning)

    reasoner.explain(
        query="Why is this value anomalous?",
        evidence=evidence,
        reasoning=reasoning,
    )

    assert evidence == evidence_before
    assert reasoning == reasoning_before


def test_same_input_is_deterministic() -> None:
    reasoner = DeterministicNaturalLanguageReasoner()

    evidence = make_evidence()
    reasoning = make_reasoning()

    first = reasoner.explain(
        query="Why is this value anomalous?",
        evidence=evidence,
        reasoning=reasoning,
    )

    second = reasoner.explain(
        query="Why is this value anomalous?",
        evidence=evidence,
        reasoning=reasoning,
    )

    assert first == second


def test_invalid_query_is_rejected() -> None:
    reasoner = DeterministicNaturalLanguageReasoner()

    try:
        reasoner.explain(
            query="",
            evidence=make_evidence(),
            reasoning=make_reasoning(),
        )
    except ValueError as exc:
        assert str(exc) == "query must be a non-empty string."
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_evidence_is_rejected() -> None:
    reasoner = DeterministicNaturalLanguageReasoner()

    try:
        reasoner.explain(
            query="Why?",
            evidence=[],
            reasoning=make_reasoning(),
        )
    except TypeError as exc:
        assert str(exc) == "evidence must be a mapping."
    else:
        raise AssertionError("Expected TypeError")

from __future__ import annotations

from copy import deepcopy

import pandas as pd


from scios.application.csv_analysis import CSVAnalysisApplication
from scios.cognitive_core.planner import Goal


GOAL = Goal(
    "Analyze the CSV dataset and explain anomalous values."
)


def _make_application(tmp_path, values) -> CSVAnalysisApplication:
    csv_path = tmp_path / "dataset.csv"
    pd.DataFrame({"value": values}).to_csv(csv_path, index=False)
    return CSVAnalysisApplication(file_path=str(csv_path))


def test_csv_application_adds_explanation_for_single_anomaly(tmp_path) -> None:
    application = _make_application(
        tmp_path,
        [10, 11, 12, 13, 14, 100],
    )

    answer = application.analyze(
        goal=GOAL,
        query="Why is value 100 an anomaly?",
    )

    assert "explanation" in answer
    assert "100.0" in answer["explanation"]
    assert "row 5" in answer["explanation"]
    assert "IQR" in answer["explanation"]


def test_csv_application_explains_multiple_anomalies(tmp_path) -> None:
    application = _make_application(
        tmp_path,
        [10, 10, 10, 10, 10, 10, 100, 1000],
    )

    answer = application.analyze(
        goal=GOAL,
        query="Explain the anomalous values.",
    )

    assert "explanation" in answer
    assert "anomalous numeric value(s)" in answer["explanation"]
    assert "row 6" in answer["explanation"]
    assert "row 7" in answer["explanation"]


def test_csv_application_explains_no_anomalies(tmp_path) -> None:
    application = _make_application(
        tmp_path,
        [18000, 19000, 20000, 21000, 22000,
         23000, 24000, 25000, 26000, 27000],
    )

    answer = application.analyze(
        goal=GOAL,
        query="Are there anomalous values?",
    )

    assert answer["reasoning"] == []
    assert answer["explanation"] == (
        "No anomalous numeric values were identified in the "
        "dataset (10 rows, 1 columns) using the available "
        "deterministic evidence."
    )


def test_csv_application_preserves_deterministic_data_when_adding_explanation(
    tmp_path,
) -> None:
    application = _make_application(
        tmp_path,
        [10, 11, 12, 13, 14, 100],
    )

    answer = application.analyze(
        goal=GOAL,
        query="Why is value 100 an anomaly?",
    )

    assert answer["outliers"]["value"]["count"] == 1
    assert answer["outliers"]["value"]["indices"] == [5]

    reasoning = answer["reasoning"]
    assert len(reasoning) == 1
    assert reasoning[0]["value"] == 100.0
    assert reasoning[0]["is_outlier"] is True
    assert reasoning[0]["evidence"]["rule"] == "IQR"


def test_csv_application_does_not_leak_internal_execution_objects(
    tmp_path,
) -> None:
    application = _make_application(
        tmp_path,
        [10, 11, 12, 13, 14, 100],
    )

    answer = application.analyze(
        goal=GOAL,
        query="Why is value 100 an anomaly?",
    )

    assert "Plan" not in answer
    assert "ExecutionGraph" not in answer
    assert "ToolResult" not in answer


def test_csv_application_passes_query_to_reasoner(tmp_path, monkeypatch) -> None:
    application = _make_application(
        tmp_path,
        [10, 11, 12, 13, 14, 100],
    )

    captured: dict[str, object] = {}

    def fake_explain(*, query, evidence, reasoning):
        captured["query"] = query
        captured["evidence"] = deepcopy(evidence)
        captured["reasoning"] = deepcopy(reasoning)
        return "captured explanation"

    monkeypatch.setattr(
        application.reasoner,
        "explain",
        fake_explain,
    )

    answer = application.analyze(
        goal=GOAL,
        query="Why is value 100 anomalous?",
    )

    assert captured["query"] == "Why is value 100 anomalous?"
    assert captured["evidence"]["rows"] == 6
    assert len(captured["reasoning"]) == 1
    assert answer["explanation"] == "captured explanation"


def test_csv_application_reasoner_failure_preserves_deterministic_answer(
    tmp_path,
    monkeypatch,
) -> None:
    application = _make_application(
        tmp_path,
        [10, 11, 12, 13, 14, 100],
    )

    def failing_explain(*, query, evidence, reasoning):
        raise RuntimeError("natural-language reasoning unavailable")

    monkeypatch.setattr(
        application.reasoner,
        "explain",
        failing_explain,
    )

    answer = application.analyze(
        goal=GOAL,
        query="Why is value 100 an anomaly?",
    )

    assert answer["rows"] == 6
    assert answer["columns"] == 1
    assert answer["outliers"]["value"]["count"] == 1
    assert answer["outliers"]["value"]["indices"] == [5]

    assert len(answer["reasoning"]) == 1
    assert answer["reasoning"][0]["is_outlier"] is True
    assert answer["reasoning"][0]["evidence"]["rule"] == "IQR"

    assert answer["explanation"] == (
        "1 anomalous numeric value(s) were identified "
        "by the deterministic reasoning layer."
    )

from __future__ import annotations

import pandas as pd

from scios.application.csv_analysis import CSVAnalysisApplication
from scios.application.csv_reasoning import EvidenceDeductiveStrategy
from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult


def test_csv_tool_evidence_can_be_consumed_by_reasoning(
    tmp_path,
) -> None:
    csv_path = tmp_path / "dataset.csv"

    dataframe = pd.DataFrame(
        {
            "value": [10, 11, 12, 13, 14, 100],
        }
    )
    dataframe.to_csv(csv_path, index=False)

    application = CSVAnalysisApplication(
        file_path=str(csv_path),
    )

    tool_result = application.tool.run(
        file_path=str(csv_path),
    )

    assert tool_result.success is True

    evidence = tool_result.value["outliers"]["value"]["evidence"][0]

    strategy = EvidenceDeductiveStrategy()

    problem = application.reasoning_problem(
        query="Why is value 100 an anomaly?",
        evidence=evidence,
    )
    assert isinstance(problem, ReasoningProblem)
    assert problem.context["evidence"]["value"] == 100.0

    reasoning_result = strategy.execute(problem)

    assert isinstance(reasoning_result, ReasoningResult)
    assert reasoning_result.problem is problem
    assert reasoning_result.accepted is True
    assert reasoning_result.conclusion["is_outlier"] is True
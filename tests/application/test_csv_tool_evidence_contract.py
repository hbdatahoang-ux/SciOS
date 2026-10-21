from __future__ import annotations

import pandas as pd

from scios.application.csv_analysis import CSVAnalysisApplication
from scios.application.csv_reasoning import EvidenceDeductiveStrategy
from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult


def test_tool_evidence_is_sufficient_for_reasoning(
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

    result = tool_result.value
    outlier = result["outliers"]["value"]
    evidence = outlier["evidence"][0]

    # The complete statistical evidence must come from the tool.
    required_evidence = {
        "column",
        "index",
        "value",
        "q1",
        "q3",
        "iqr",
        "lower_bound",
        "upper_bound",
        "rule",
    }

    assert required_evidence <= set(evidence)

    problem = application.reasoning_problem(
        query="Why is value 100 an anomaly?",
        evidence=evidence,
    )

    assert isinstance(problem, ReasoningProblem)
    assert problem.context["evidence"] == evidence

    reasoning_result = EvidenceDeductiveStrategy().execute(problem)

    assert isinstance(reasoning_result, ReasoningResult)
    assert reasoning_result.accepted is True
    assert reasoning_result.conclusion["is_outlier"] is True
    assert reasoning_result.conclusion["value"] == evidence["value"]

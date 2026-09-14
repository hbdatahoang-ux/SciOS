from __future__ import annotations

import pandas as pd

from scios.application.csv_analysis import CSVAnalysisApplication
from scios.cognitive_core.planner.goal import Goal


def test_csv_product_vertical_slice_end_to_end(tmp_path) -> None:
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

    goal = Goal(
        "Analyze the CSV dataset and explain anomalous values.",
    )

    answer = application.analyze(
        goal=goal,
        query="Why is value 100 an anomaly?",
    )

    assert answer["goal"] == goal.description

    assert answer["rows"] == 6
    assert answer["columns"] == 1
    assert answer["column_names"] == ["value"]

    outlier = answer["outliers"]["value"]

    assert outlier["count"] == 1
    assert outlier["indices"] == [5]

    assert len(answer["reasoning"]) == 1

    conclusion = answer["reasoning"][0]

    assert conclusion["column"] == "value"
    assert conclusion["index"] == 5
    assert conclusion["value"] == 100.0
    assert conclusion["is_outlier"] is True

    assert conclusion["evidence"]["rule"] == "IQR"

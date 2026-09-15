from __future__ import annotations

import pandas as pd
from fastapi.testclient import TestClient

from scios.api.server import create_app


def test_csv_analyze_api_end_to_end(tmp_path) -> None:
    csv_path = tmp_path / "dataset.csv"

    dataframe = pd.DataFrame(
        {
            "value": [10, 11, 12, 13, 14, 100],
        }
    )
    dataframe.to_csv(csv_path, index=False)

    client = TestClient(create_app())

    response = client.post(
        "/csv/analyze",
        json={
            "file_path": str(csv_path),
            "query": "Why are there anomalous values?",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["goal"] == (
        "Analyze the CSV dataset and explain anomalous values."
    )
    assert payload["rows"] == 6
    assert payload["columns"] == 1
    assert payload["column_names"] == ["value"]
    assert payload["missing"] == {"value": 0}

    outlier = payload["outliers"]["value"]

    assert outlier["count"] == 1
    assert outlier["indices"] == [5]
    assert len(outlier["evidence"]) == 1

    evidence = outlier["evidence"][0]

    assert evidence["column"] == "value"
    assert evidence["index"] == 5
    assert evidence["value"] == 100.0
    assert evidence["rule"] == "IQR"

    assert len(payload["reasoning"]) == 1

    reasoning = payload["reasoning"][0]

    assert reasoning["column"] == "value"
    assert reasoning["index"] == 5
    assert reasoning["value"] == 100.0
    assert reasoning["is_outlier"] is True
    assert reasoning["evidence"]["rule"] == "IQR"

    assert "Plan" not in payload
    assert "ExecutionGraph" not in payload
    assert "ToolResult" not in payload

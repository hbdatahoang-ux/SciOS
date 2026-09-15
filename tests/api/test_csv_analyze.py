from __future__ import annotations

import pandas as pd
import pytest
from fastapi.testclient import TestClient

import scios.api.routes as routes

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

    assert "explanation" in payload
    assert "100.0" in payload["explanation"]
    assert "row 5" in payload["explanation"]
    assert "IQR" in payload["explanation"]

    assert "Plan" not in payload
    assert "ExecutionGraph" not in payload
    assert "ToolResult" not in payload


def test_csv_analyze_api_missing_file_returns_404(tmp_path) -> None:
    csv_path = tmp_path / "missing.csv"

    client = TestClient(create_app())

    response = client.post(
        "/csv/analyze",
        json={
            "file_path": str(csv_path),
            "query": "Why are there anomalous values?",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "CSV file not found."}


def test_csv_analyze_api_empty_file_returns_400(tmp_path) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("", encoding="utf-8")

    client = TestClient(create_app())

    response = client.post(
        "/csv/analyze",
        json={
            "file_path": str(csv_path),
            "query": "Why are there anomalous values?",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "CSV file is empty."}


def test_csv_analyze_api_malformed_file_returns_400(tmp_path) -> None:
    csv_path = tmp_path / "malformed.csv"
    csv_path.write_text(
        "value,other\n1,2,\"unterminated\n",
        encoding="utf-8",
    )

    client = TestClient(create_app())

    response = client.post(
        "/csv/analyze",
        json={
            "file_path": str(csv_path),
            "query": "Why are there anomalous values?",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "CSV file is malformed."}


def test_csv_analyze_api_unexpected_failure_returns_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_analyze(self, *, goal, query):
        raise RuntimeError("CSV analysis execution failed.") from ValueError(
            "unexpected failure"
        )

    monkeypatch.setattr(
        routes.CSVAnalysisApplication,
        "analyze",
        fail_analyze,
    )

    client = TestClient(create_app())

    response = client.post(
        "/csv/analyze",
        json={
            "file_path": "unused.csv",
            "query": "Why are there anomalous values?",
        },
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "CSV analysis failed."}

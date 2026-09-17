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

    assert isinstance(payload["analysis_run_id"], str)
    assert payload["analysis_run_id"]

    assert isinstance(payload["dataset_hash"], str)
    assert len(payload["dataset_hash"]) == 64
    assert all(
        character in "0123456789abcdef"
        for character in payload["dataset_hash"]
    )

    assert "Plan" not in payload
    assert "ExecutionGraph" not in payload
    assert "ToolResult" not in payload


def test_csv_analyze_api_reproducibility_identifiers(tmp_path) -> None:
    csv_path = tmp_path / "dataset.csv"

    raw_csv = b"value\n10\n11\n12\n13\n14\n100\n"
    csv_path.write_bytes(raw_csv)

    client = TestClient(create_app())

    request = {
        "file_path": str(csv_path),
        "query": "Why are there anomalous values?",
    }

    first = client.post("/csv/analyze", json=request)
    second = client.post("/csv/analyze", json=request)

    assert first.status_code == 200
    assert second.status_code == 200

    first_payload = first.json()
    second_payload = second.json()

    assert first_payload["dataset_hash"] == second_payload["dataset_hash"]
    assert first_payload["analysis_run_id"] != second_payload["analysis_run_id"]

    assert first_payload["rows"] == second_payload["rows"]
    assert first_payload["columns"] == second_payload["columns"]
    assert first_payload["column_names"] == second_payload["column_names"]
    assert first_payload["missing"] == second_payload["missing"]
    assert first_payload["outliers"] == second_payload["outliers"]
    assert first_payload["reasoning"] == second_payload["reasoning"]


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

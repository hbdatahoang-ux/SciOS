"""Focused tests for the local Community CSV adapter."""
import hashlib
import json

import pytest

from scios.community.csv_adapter import (
    MAX_CSV_BYTES, analyze_csv, report_json, report_markdown,
)

CSV = b"value\n10\n11\n12\n13\n14\n100\n"
QUESTION = "Which values are anomalous?"


def test_local_csv_analysis_and_exports():
    report = analyze_csv(CSV, filename="example.csv", query=QUESTION)
    assert report["dataset"]["sha256"] == hashlib.sha256(CSV).hexdigest()
    assert report["result"]["dataset_hash"] == report["dataset"]["sha256"]
    assert report["result"]["outliers"]["value"]["indices"] == [5]
    assert report["operation"] == {"name": "csv_analysis", "version": "0.1.0"}
    assert report["method"]["factor"] == 1.5
    assert report["analysis_run_id"] == report["result"]["analysis_run_id"]
    assert json.loads(report_json(report)) == report
    markdown = report_markdown(report)
    assert report["dataset"]["sha256"] in markdown
    assert "Q1=" in markdown and "IQR=" in markdown
    assert "not scientific proof" in markdown


def test_same_input_has_same_hash_but_unique_run_ids():
    first = analyze_csv(CSV, filename="data.csv", query=QUESTION)
    second = analyze_csv(CSV, filename="data.csv", query=QUESTION)
    assert first["dataset"]["sha256"] == second["dataset"]["sha256"]
    assert first["analysis_run_id"] != second["analysis_run_id"]
    assert first["result"]["outliers"] == second["result"]["outliers"]


@pytest.mark.parametrize("data,name,question", [
    (b"", "data.csv", QUESTION),
    (b"   ", "data.csv", QUESTION),
    (CSV, "data.txt", QUESTION),
    (CSV, "data.csv", ""),
    (b"x" * (MAX_CSV_BYTES + 1), "data.csv", QUESTION),
])
def test_invalid_uploads_are_rejected(data, name, question):
    with pytest.raises(ValueError):
        analyze_csv(data, filename=name, query=question)


def test_filename_is_not_used_as_local_path():
    report = analyze_csv(CSV, filename="../../outside.csv", query=QUESTION)
    assert report["dataset"]["filename"] == "outside.csv"

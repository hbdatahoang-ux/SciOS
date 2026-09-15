from __future__ import annotations

import pandas as pd
import pytest

import scios.cli.csv_analysis as cli
from scios.cli.csv_analysis import main


def test_csv_analysis_cli_end_to_end(tmp_path, capsys) -> None:
    csv_path = tmp_path / "dataset.csv"

    dataframe = pd.DataFrame(
        {
            "value": [10, 11, 12, 13, 14, 100],
        }
    )
    dataframe.to_csv(csv_path, index=False)

    exit_code = main(
        [
            "--file",
            str(csv_path),
            "--query",
            "Why are there anomalous values?",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "SciOS CSV Analysis" in captured.out
    assert "Rows: 6" in captured.out
    assert "Columns: 1" in captured.out
    assert "value" in captured.out
    assert "row: 5" in captured.out
    assert "value: 100.0" in captured.out
    assert "rule: IQR" in captured.out
    assert "Explanation" in captured.out
    assert "100.0" in captured.out
    assert "row 5" in captured.out
    assert "IQR" in captured.out
    assert "1 anomalous value(s) detected." in captured.out

    assert "Plan(" not in captured.out
    assert "ExecutionGraph" not in captured.out


def test_csv_analysis_cli_missing_file_returns_1(
    tmp_path,
    capsys,
) -> None:
    csv_path = tmp_path / "missing.csv"

    exit_code = main(
        [
            "--file",
            str(csv_path),
            "--query",
            "Why are there anomalous values?",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "Error: CSV file not found.\n"


def test_csv_analysis_cli_empty_file_returns_1(
    tmp_path,
    capsys,
) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("", encoding="utf-8")

    exit_code = main(
        [
            "--file",
            str(csv_path),
            "--query",
            "Why are there anomalous values?",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "Error: CSV file is empty.\n"


def test_csv_analysis_cli_malformed_file_returns_1(
    tmp_path,
    capsys,
) -> None:
    csv_path = tmp_path / "malformed.csv"
    csv_path.write_text(
        "value,other\n1,2,\"unterminated\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--file",
            str(csv_path),
            "--query",
            "Why are there anomalous values?",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "Error: CSV file is malformed.\n"


def test_csv_analysis_cli_unexpected_failure_returns_1(
    monkeypatch: pytest.MonkeyPatch,
    capsys,
) -> None:
    def fail_analyze(self, *, goal, query):
        raise RuntimeError("CSV analysis execution failed.") from ValueError(
            "unexpected failure"
        )

    monkeypatch.setattr(
        cli.CSVAnalysisApplication,
        "analyze",
        fail_analyze,
    )

    exit_code = main(
        [
            "--file",
            "unused.csv",
            "--query",
            "Why are there anomalous values?",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "Error: CSV analysis failed.\n"

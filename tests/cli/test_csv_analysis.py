from __future__ import annotations

import pandas as pd

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

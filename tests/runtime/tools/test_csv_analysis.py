from pathlib import Path

import pytest

from scios.runtime.tools.csv_analysis import CSVAnalysisTool


def write_csv(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "data.csv"
    path.write_text(content, encoding="utf-8")
    return path


def test_tool_identity():
    tool = CSVAnalysisTool()

    assert tool.name == "csv_analysis"
    assert tool.version == "0.1.0"


def test_schema_contract():
    tool = CSVAnalysisTool()

    schema = tool.schema()

    assert schema["required"] == ["file_path"]


def test_basic_dataset_summary(tmp_path):
    path = write_csv(
        tmp_path,
        "value,score\n10,1.0\n20,2.0\n30,3.0\n",
    )

    result = CSVAnalysisTool().run(
        file_path=str(path)
    )

    assert result.success

    value = result.value

    assert value["rows"] == 3
    assert value["columns"] == 2
    assert value["column_names"] == ["value", "score"]


def test_missing_values(tmp_path):
    path = write_csv(
        tmp_path,
        "value,score\n10,1.0\n,2.0\n30,\n",
    )

    result = CSVAnalysisTool().run(
        file_path=str(path)
    )

    assert result.success

    value = result.value

    assert value["missing"] == {
        "value": 1,
        "score": 1,
    }


def test_numeric_summary(tmp_path):
    path = write_csv(
        tmp_path,
        "value\n10\n20\n30\n",
    )

    result = CSVAnalysisTool().run(
        file_path=str(path)
    )

    assert result.success

    summary = result.value["numeric_summary"]["value"]

    assert summary["count"] == 3
    assert summary["mean"] == pytest.approx(20.0)
    assert summary["min"] == pytest.approx(10.0)
    assert summary["max"] == pytest.approx(30.0)


def test_iqr_outlier_detection(tmp_path):
    path = write_csv(
        tmp_path,
        "value\n10\n11\n12\n13\n14\n100\n",
    )

    result = CSVAnalysisTool().run(
        file_path=str(path)
    )

    assert result.success

    outlier = result.value["outliers"]["value"]

    assert outlier["count"] == 1
    assert outlier["indices"] == [5]


def test_missing_file_returns_failed_tool_result(tmp_path):
    path = tmp_path / "missing.csv"

    result = CSVAnalysisTool().run(
        file_path=str(path)
    )

    assert not result.success
    assert result.error is not None

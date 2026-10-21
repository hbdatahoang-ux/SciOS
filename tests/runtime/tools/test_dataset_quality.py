from pathlib import Path

import pytest

from scios.runtime.tools.dataset_quality import DatasetQualityTool


def write_csv(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "data.csv"
    path.write_text(content, encoding="utf-8")
    return path


def test_tool_identity():
    tool = DatasetQualityTool()

    assert tool.name == "dataset_quality"
    assert tool.version == "0.1.0"


def test_schema_contract():
    tool = DatasetQualityTool()

    schema = tool.schema()

    assert schema["required"] == ["file_path"]
    assert schema["properties"]["file_path"]["type"] == "string"


def test_validate_contract():
    tool = DatasetQualityTool()

    assert tool.validate(file_path="data.csv")
    assert not tool.validate(file_path="")
    assert not tool.validate(file_path="   ")
    assert not tool.validate(file_path=None)


def test_complete_quality_profile(tmp_path):
    path = write_csv(
        tmp_path,
        "id,age,group,active\n"
        "1,20,A,True\n"
        "2,25,B,False\n"
        "3,30,A,True\n"
        "4,35,B,False\n"
        "5,40,A,True\n",
    )

    result = DatasetQualityTool().run(
        file_path=str(path)
    )

    assert result.success

    value = result.value

    assert value["rows"] == 5
    assert value["columns"] == 4
    assert value["column_names"] == [
        "id",
        "age",
        "group",
        "active",
    ]

    profile = value["columns_profile"]

    assert profile["id"]["kind"] == "numeric"
    assert profile["age"]["kind"] == "numeric"
    assert profile["group"]["kind"] == "categorical/text"
    assert profile["active"]["kind"] == "boolean"

    assert profile["id"]["missing_count"] == 0
    assert profile["age"]["missing_count"] == 0
    assert profile["group"]["missing_count"] == 0
    assert profile["active"]["missing_count"] == 0

    assert profile["id"]["unique_count"] == 5
    assert profile["age"]["unique_count"] == 5
    assert profile["group"]["unique_count"] == 2
    assert profile["active"]["unique_count"] == 2

    assert profile["id"]["is_constant"] is False
    assert profile["age"]["is_constant"] is False
    assert profile["group"]["is_constant"] is False
    assert profile["active"]["is_constant"] is False

    assert value["duplicate_rows"] == {
        "count": 0,
        "fraction": 0.0,
    }


def test_missing_values(tmp_path):
    path = write_csv(
        tmp_path,
        "id,age,group\n"
        "1,20,A\n"
        "2,,B\n"
        "3,30,\n"
        "4,,A\n"
        "5,40,B\n",
    )

    result = DatasetQualityTool().run(
        file_path=str(path)
    )

    assert result.success

    profile = result.value["columns_profile"]

    assert profile["age"]["missing_count"] == 2
    assert profile["age"]["missing_fraction"] == pytest.approx(0.4)

    assert profile["group"]["missing_count"] == 1
    assert profile["group"]["missing_fraction"] == pytest.approx(0.2)

    assert profile["id"]["missing_count"] == 0
    assert profile["id"]["missing_fraction"] == 0.0


def test_duplicate_rows(tmp_path):
    path = write_csv(
        tmp_path,
        "id,value\n"
        "1,10\n"
        "2,20\n"
        "2,20\n"
        "3,30\n"
        "3,30\n",
    )

    result = DatasetQualityTool().run(
        file_path=str(path)
    )

    assert result.success

    assert result.value["duplicate_rows"] == {
        "count": 2,
        "fraction": pytest.approx(0.4),
    }


def test_constant_columns(tmp_path):
    path = write_csv(
        tmp_path,
        "id,constant,variable\n"
        "1,X,A\n"
        "2,X,B\n"
        "3,X,C\n"
        "4,X,D\n",
    )

    result = DatasetQualityTool().run(
        file_path=str(path)
    )

    assert result.success

    profile = result.value["columns_profile"]

    assert profile["constant"]["unique_count"] == 1
    assert profile["constant"]["is_constant"] is True

    assert profile["variable"]["unique_count"] == 4
    assert profile["variable"]["is_constant"] is False


def test_mixed_column_types(tmp_path):
    path = write_csv(
        tmp_path,
        "number,flag,label\n"
        "1,True,A\n"
        "2,False,B\n"
        "3,True,A\n"
        "4,False,C\n",
    )

    result = DatasetQualityTool().run(
        file_path=str(path)
    )

    assert result.success

    profile = result.value["columns_profile"]

    assert profile["number"]["kind"] == "numeric"
    assert profile["flag"]["kind"] == "boolean"
    assert profile["label"]["kind"] == "categorical/text"


def test_empty_dataset(tmp_path):
    path = write_csv(
        tmp_path,
        "id,value,label\n",
    )

    result = DatasetQualityTool().run(
        file_path=str(path)
    )

    assert result.success

    value = result.value

    assert value["rows"] == 0
    assert value["columns"] == 3

    profile = value["columns_profile"]

    for column in ("id", "value", "label"):
        assert profile[column]["missing_count"] == 0
        assert profile[column]["missing_fraction"] == 0.0
        assert profile[column]["unique_count"] == 0
        assert profile[column]["is_constant"] is True

    assert value["duplicate_rows"] == {
        "count": 0,
        "fraction": 0.0,
    }


def test_quality_evidence_shape(tmp_path):
    path = write_csv(
        tmp_path,
        "id,value,constant\n"
        "1,10,X\n"
        "2,,X\n"
        "2,,X\n"
        "3,30,X\n",
    )

    result = DatasetQualityTool().run(
        file_path=str(path)
    )

    assert result.success

    value = result.value

    assert set(value) == {
        "rows",
        "columns",
        "column_names",
        "columns_profile",
        "duplicate_rows",
    }

    for column in value["column_names"]:
        assert set(value["columns_profile"][column]) == {
            "dtype",
            "kind",
            "missing_count",
            "missing_fraction",
            "unique_count",
            "is_constant",
        }

    assert set(value["duplicate_rows"]) == {
        "count",
        "fraction",
    }


def test_missing_file_returns_failed_tool_result(tmp_path):
    path = tmp_path / "missing.csv"

    result = DatasetQualityTool().run(
        file_path=str(path)
    )

    assert not result.success
    assert result.error is not None

from pathlib import Path

from scios.runtime.tools.csv_analysis import CSVAnalysisTool
from scios.runtime.tools.registry import ToolRegistry


def write_csv(tmp_path: Path) -> Path:
    path = tmp_path / "data.csv"
    path.write_text(
        "value\n10\n11\n12\n13\n14\n100\n",
        encoding="utf-8",
    )
    return path


def test_csv_analysis_registers_in_tool_registry():
    registry = ToolRegistry()
    tool = CSVAnalysisTool()

    registered = registry.register(tool)

    assert registered is tool
    assert registry.exists("csv_analysis")
    assert registry.get("csv_analysis") is tool
    assert registry.count == 1


def test_csv_analysis_runs_through_registry(tmp_path):
    registry = ToolRegistry()
    registry.register(CSVAnalysisTool())

    tool = registry.require("csv_analysis")
    result = tool.run(
        file_path=str(write_csv(tmp_path))
    )

    assert result.success
    assert result.value["rows"] == 6
    assert result.value["outliers"]["value"]["count"] == 1
    assert result.value["outliers"]["value"]["indices"] == [5]

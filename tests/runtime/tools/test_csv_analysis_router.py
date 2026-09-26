from pathlib import Path

from scios.runtime.agent.tool_router import ToolRouter
from scios.runtime.tools.csv_analysis import CSVAnalysisTool
from scios.runtime.tools.result import ToolResult


def test_csv_analysis_routes_through_tool_router(tmp_path: Path):
    path = tmp_path / "data.csv"
    path.write_text(
        "value,score\n10,1.0\n11,2.0\n12,3.0\n13,4.0\n14,5.0\n100,6.0\n",
        encoding="utf-8",
    )

    router = ToolRouter()
    router.register(CSVAnalysisTool())

    result = router.route(
        "csv_analysis",
        file_path=str(path),
    )

    assert isinstance(result, ToolResult)
    assert result.success

    assert result.value["rows"] == 6
    assert result.value["columns"] == 2
    assert result.value["outliers"]["value"]["count"] == 1
    assert result.value["outliers"]["value"]["indices"] == [5]

    assert router.executions == 1
    assert router.executor.executions == 1

from pathlib import Path

from scios.runtime.agent.agent import Agent
from scios.runtime.agent.tool_router import ToolRouter
from scios.runtime.tools.csv_analysis import CSVAnalysisTool


class CSVDecisionProvider:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def create_plan(self, goal: str) -> dict:
        return {
            "tool": "csv_analysis",
            "args": {
                "file_path": self.file_path,
            },
        }


def test_agent_runs_csv_analysis_through_runtime_tool_path(
    tmp_path: Path,
):
    path = tmp_path / "data.csv"
    path.write_text(
        "value\n10\n11\n12\n13\n14\n100\n",
        encoding="utf-8",
    )

    router = ToolRouter()
    router.register(CSVAnalysisTool())

    agent = Agent(
        name="csv-agent",
        planner=CSVDecisionProvider(str(path)),
        router=router,
    )

    result = agent.run(
        "analyze CSV anomalies"
    )

    assert result["status"] == "completed"
    assert result["task"] == "analyze CSV anomalies"

    value = result["result"]["value"]
    assert value["rows"] == 6
    assert value["columns"] == 1
    assert value["outliers"]["value"]["count"] == 1
    assert value["outliers"]["value"]["indices"] == [5]

    assert router.executions == 1
    assert router.executor.executions == 1

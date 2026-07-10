# __init__.py
# Entry point cho SciOS Cognitive Core Pipeline

from typing import Any, Dict, List
from scios.cognitive_core.pipeline.graph.graph import Graph
from scios.cognitive_core.pipeline.graph.node import GraphNode
from scios.cognitive_core.pipeline.graph.edge import GraphEdge

# Import các stage
from scios.cognitive_core.pipeline.stages.memory_stage import MemoryStage
from scios.cognitive_core.pipeline.stages.reasoning_stage import ReasoningStage
from scios.cognitive_core.pipeline.stages.planning_stage import PlanningStage
from scios.cognitive_core.pipeline.stages.tool_stage import ToolStage
from scios.cognitive_core.pipeline.stages.reflection_stage import ReflectionStage
from scios.cognitive_core.pipeline.stages.output_stage import OutputStage

class CognitivePipeline:
    """
    CognitivePipeline gom các stage và graph thành một pipeline hoàn chỉnh.
    Nó quản lý DAG, chạy dữ liệu qua các stage, và xuất kết quả cuối cùng.
    """

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.graph = Graph(name="cognitive_pipeline")

        # Khởi tạo các stage mặc định
        self.memory_stage = MemoryStage()
        self.reasoning_stage = ReasoningStage()
        self.planning_stage = PlanningStage()
        self.tool_stage = ToolStage()
        self.reflection_stage = ReflectionStage()
        self.output_stage = OutputStage()

        # Thêm node vào graph
        self.graph.add_node(GraphNode("memory", self.memory_stage))
        self.graph.add_node(GraphNode("reasoning", self.reasoning_stage))
        self.graph.add_node(GraphNode("planning", self.planning_stage))
        self.graph.add_node(GraphNode("tool", self.tool_stage))
        self.graph.add_node(GraphNode("reflection", self.reflection_stage))
        self.graph.add_node(GraphNode("output", self.output_stage))

        # Định nghĩa dependency (DAG)
        self.graph.add_edge("memory", "reasoning")
        self.graph.add_edge("reasoning", "planning")
        self.graph.add_edge("planning", "tool")
        self.graph.add_edge("tool", "reflection")
        self.graph.add_edge("reflection", "output")

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chạy dữ liệu qua pipeline theo DAG.
        """
        return self.graph.execute(data)

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin pipeline.
        """
        return self.graph.summary()

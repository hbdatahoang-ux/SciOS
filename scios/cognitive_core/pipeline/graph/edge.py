# edge.py
# Graph Edge cho SciOS Cognitive Core - DAG Execution

from typing import Any, Dict

class GraphEdge:
    """
    GraphEdge đại diện cho một cạnh (edge) trong ExecutionGraph.
    Nó mô tả quan hệ giữa node nguồn và node đích, có thể kèm metadata.
    """

    def __init__(self, source: str, target: str, metadata: Dict[str, Any] | None = None) -> None:
        self.source = source
        self.target = target
        self.metadata = metadata or {}

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin edge.
        """
        return {
            "source": self.source,
            "target": self.target,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return f"GraphEdge({self.source} -> {self.target}, metadata={self.metadata})"

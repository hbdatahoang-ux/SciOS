# node.py
# Graph Node cho SciOS Cognitive Core - DAG Execution

from typing import Any, Dict, List, Callable

class GraphNode:
    """
    GraphNode đại diện cho một node trong ExecutionGraph.
    Mỗi node wrap một stage hoặc processor, có thể chứa metadata và dependencies.
    """

    def __init__(self, name: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]], metadata: Dict[str, Any] | None = None) -> None:
        self.name = name
        self.handler = handler
        self.metadata = metadata or {}
        self.dependencies: List[str] = []

    def add_dependency(self, node_name: str) -> None:
        """
        Thêm dependency cho node này.
        """
        if node_name not in self.dependencies:
            self.dependencies.append(node_name)

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chạy dữ liệu qua handler của node.
        """
        if callable(self.handler):
            return self.handler(data)
        elif hasattr(self.handler, "process"):
            return self.handler.process(data)
        else:
            raise TypeError(f"Handler cho node '{self.name}' không hợp lệ.")

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin node.
        """
        return {
            "node": self.name,
            "dependencies": self.dependencies,
            "handler": getattr(self.handler, "__name__", type(self.handler).__name__),
            "metadata": self.metadata,
        }

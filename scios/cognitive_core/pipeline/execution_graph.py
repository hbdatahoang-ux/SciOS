# execution_graph.py
# DAG Executor cho SciOS Cognitive Core - Pipeline

from typing import Any, Dict, List, Callable, Set

class ExecutionGraph:
    """
    ExecutionGraph quản lý DAG của các stage trong CognitivePipeline.
    Cho phép định nghĩa node (stage), dependency, và chạy theo thứ tự hợp lệ.
    """

    def __init__(self, name: str = "execution_graph") -> None:
        self.name = name
        self.nodes: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self.edges: Dict[str, List[str]] = {}  # dependency mapping

    def add_node(self, name: str, stage: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """
        Thêm một node (stage) vào graph.
        """
        self.nodes[name] = stage
        if name not in self.edges:
            self.edges[name] = []

    def add_dependency(self, node: str, depends_on: str) -> None:
        """
        Khai báo dependency: node phụ thuộc vào depends_on.
        """
        if node not in self.edges:
            self.edges[node] = []
        self.edges[node].append(depends_on)

    def _topological_sort(self) -> List[str]:
        """
        Sắp xếp các node theo thứ tự hợp lệ (topological order).
        """
        visited: Set[str] = set()
        stack: List[str] = []
        temp: Set[str] = set()

        def visit(node: str):
            if node in temp:
                raise RuntimeError(f"Cycle detected in DAG at node {node}")
            if node not in visited:
                temp.add(node)
                for dep in self.edges.get(node, []):
                    visit(dep)
                temp.remove(node)
                visited.add(node)
                stack.append(node)

        for node in self.nodes:
            visit(node)

        return stack[::-1]  # reverse to get correct order

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chạy dữ liệu qua DAG theo thứ tự topological.
        """
        order = self._topological_sort()
        result = data
        for node in order:
            stage = self.nodes[node]
            if callable(stage):
                result = stage(result)
            elif hasattr(stage, "process"):
                result = stage.process(result)
            else:
                raise TypeError(f"Stage {node} không hợp lệ.")
        return result

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin DAG.
        """
        return {
            "graph": self.name,
            "nodes": list(self.nodes.keys()),
            "edges": self.edges,
        }

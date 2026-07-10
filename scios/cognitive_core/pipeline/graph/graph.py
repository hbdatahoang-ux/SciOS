# graph.py
# Graph Manager cho SciOS Cognitive Core - DAG Execution

from typing import Any, Dict, List
from scios.cognitive_core.pipeline.graph.node import GraphNode
from scios.cognitive_core.pipeline.graph.edge import GraphEdge

class Graph:
    """
    Graph quản lý DAG gồm các node và edge.
    Cho phép thêm node, edge, kiểm tra dependency, và thực thi pipeline.
    """

    def __init__(self, name: str = "execution_graph") -> None:
        self.name = name
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

    def add_node(self, node: GraphNode) -> None:
        """
        Thêm node vào graph.
        """
        self.nodes[node.name] = node

    def add_edge(self, source: str, target: str, metadata: Dict[str, Any] | None = None) -> None:
        """
        Thêm edge (dependency) giữa hai node.
        """
        if source not in self.nodes or target not in self.nodes:
            raise ValueError(f"Node '{source}' hoặc '{target}' chưa tồn tại trong graph.")
        edge = GraphEdge(source, target, metadata)
        self.edges.append(edge)
        self.nodes[target].add_dependency(source)

    def _topological_sort(self) -> List[str]:
        """
        Sắp xếp node theo thứ tự hợp lệ (topological order).
        """
        visited = set()
        stack: List[str] = []
        temp = set()

        def visit(node_name: str):
            if node_name in temp:
                raise RuntimeError(f"Cycle detected tại node {node_name}")
            if node_name not in visited:
                temp.add(node_name)
                for dep in self.nodes[node_name].dependencies:
                    visit(dep)
                temp.remove(node_name)
                visited.add(node_name)
                stack.append(node_name)

        for node_name in self.nodes:
            visit(node_name)

        return stack[::-1]

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chạy dữ liệu qua DAG theo thứ tự topological.
        """
        order = self._topological_sort()
        result = data
        for node_name in order:
            result = self.nodes[node_name].process(result)
        return result

    def summary(self) -> Dict[str, Any]:
        """
        Trả về thông tin graph.
        """
        return {
            "graph": self.name,
            "nodes": [node.summary() for node in self.nodes.values()],
            "edges": [edge.summary() for edge in self.edges],
        }

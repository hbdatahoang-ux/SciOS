from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from scios.execution.node.node import ExecutionNode
from scios.execution.graph.edge import ExecutionEdge


@dataclass
class ExecutionGraph:
    """
    ExecutionGraph = Directed graph of ExecutionNodes and ExecutionEdges.
    Represents program IR for scheduling and execution.
    """

    graph_id: UUID = field(default_factory=uuid4)
    nodes: Dict[UUID, ExecutionNode] = field(default_factory=dict)
    edges: List[ExecutionEdge] = field(default_factory=list)

    # =========================================================
    # Node API
    # =========================================================

    def add_node(self, node: ExecutionNode) -> None:
        self.nodes[node.node_id] = node

    def get_node(self, node_id: UUID) -> Optional[ExecutionNode]:
        return self.nodes.get(node_id)

    def remove_node(self, node_id: UUID) -> None:
        if node_id in self.nodes:
            del self.nodes[node_id]
            # Remove edges connected to this node
            self.edges = [e for e in self.edges if e.source_id != node_id and e.target_id != node_id]

    # =========================================================
    # Edge API
    # =========================================================

    def add_edge(self, edge: ExecutionEdge) -> None:
        self.edges.append(edge)

    def get_edges_from(self, node_id: UUID) -> List[ExecutionEdge]:
        return [e for e in self.edges if e.source_id == node_id]

    def get_edges_to(self, node_id: UUID) -> List[ExecutionEdge]:
        return [e for e in self.edges if e.target_id == node_id]

    def remove_edge(self, edge: ExecutionEdge) -> None:
        if edge in self.edges:
            self.edges.remove(edge)

    # =========================================================
    # Traversal / Scheduling
    # =========================================================

    def roots(self) -> List[ExecutionNode]:
        """
        Return nodes with no incoming edges.
        """
        targets = {e.target_id for e in self.edges}
        return [n for n in self.nodes.values() if n.node_id not in targets]

    def leaves(self) -> List[ExecutionNode]:
        """
        Return nodes with no outgoing edges.
        """
        sources = {e.source_id for e in self.edges}
        return [n for n in self.nodes.values() if n.node_id not in sources]

    def successors(self, node_id: UUID) -> List[ExecutionNode]:
        """
        Return successor nodes of given node.
        """
        return [self.nodes[e.target_id] for e in self.edges if e.source_id == node_id]

    def predecessors(self, node_id: UUID) -> List[ExecutionNode]:
        """
        Return predecessor nodes of given node.
        """
        return [self.nodes[e.source_id] for e in self.edges if e.target_id == node_id]

    # =========================================================
    # Serialization
    # =========================================================

    def to_dict(self) -> dict:
        return {
            "graph_id": str(self.graph_id),
            "nodes": {str(nid): node.to_dict() for nid, node in self.nodes.items()},
            "edges": [e.to_dict() for e in self.edges],
        }

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple
from uuid import UUID, uuid4


@dataclass
class KnowledgeGraph:
    """
    KnowledgeGraph = Stores knowledge as nodes and relationships.
    """

    graph_id: UUID = field(default_factory=uuid4)
    nodes: Dict[str, Any] = field(default_factory=dict)
    edges: List[Tuple[str, str, str]] = field(default_factory=list)
    # edge format: (source, relation, target)

    # =========================================================
    # Core API
    # =========================================================

    def add_node(self, node_id: str, data: Any) -> None:
        """
        Add a node (concept/fact) to the graph.
        """
        self.nodes[node_id] = data

    def add_edge(self, source: str, relation: str, target: str) -> None:
        """
        Add a relationship between two nodes.
        """
        if source in self.nodes and target in self.nodes:
            self.edges.append((source, relation, target))

    def get_node(self, node_id: str) -> Any:
        """
        Retrieve node data.
        """
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> List[Tuple[str, str]]:
        """
        Get neighbors of a node with relations.
        """
        neighbors = []
        for s, r, t in self.edges:
            if s == node_id:
                neighbors.append((r, t))
            elif t == node_id:
                neighbors.append((r, s))
        return neighbors

    def find_relation(self, source: str, target: str) -> List[str]:
        """
        Find relations between two nodes.
        """
        return [r for s, r, t in self.edges if s == source and t == target]

    # =========================================================
    # Utility
    # =========================================================

    def all_nodes(self) -> Dict[str, Any]:
        """
        Return all nodes.
        """
        return dict(self.nodes)

    def all_edges(self) -> List[Tuple[str, str, str]]:
        """
        Return all edges.
        """
        return list(self.edges)

    def clear(self) -> None:
        """
        Clear graph.
        """
        self.nodes.clear()
        self.edges.clear()

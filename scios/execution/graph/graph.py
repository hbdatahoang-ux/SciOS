from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from scios.execution.graph.edge import ExecutionEdge
from scios.execution.node.node import ExecutionNode


class ExecutionGraphError(ValueError):
    """Raised when an ExecutionGraph invariant is violated."""


@dataclass
class ExecutionGraph:
    """
    Canonical Execution IR graph.

    ExecutionGraph owns node/edge topology and maintains a valid DAG
    after every successful public mutation.
    """

    graph_id: UUID = field(default_factory=uuid4)
    nodes: dict[UUID, ExecutionNode] = field(default_factory=dict)
    edges: list[ExecutionEdge] = field(default_factory=list)

    # =========================================================
    # Node API
    # =========================================================

    def add_node(self, node: ExecutionNode) -> None:
        if not isinstance(node, ExecutionNode):
            raise TypeError("node must be an ExecutionNode")

        if node.node_id in self.nodes:
            raise ExecutionGraphError(
                f"Node already exists: {node.node_id}"
            )

        self.nodes[node.node_id] = node

    def get_node(self, node_id: UUID) -> ExecutionNode | None:
        return self.nodes.get(node_id)

    def remove_node(self, node_id: UUID) -> None:
        if node_id not in self.nodes:
            return

        del self.nodes[node_id]

        self.edges = [
            edge
            for edge in self.edges
            if edge.source_id != node_id
            and edge.target_id != node_id
        ]

    # =========================================================
    # Edge API
    # =========================================================

    def add_edge(self, edge: ExecutionEdge) -> None:
        if not isinstance(edge, ExecutionEdge):
            raise TypeError("edge must be an ExecutionEdge")

        if edge.source_id not in self.nodes:
            raise ExecutionGraphError(
                f"Edge source node does not exist: {edge.source_id}"
            )

        if edge.target_id not in self.nodes:
            raise ExecutionGraphError(
                f"Edge target node does not exist: {edge.target_id}"
            )

        if edge.is_self_loop():
            raise ExecutionGraphError(
                f"Self-loop is not allowed: {edge.source_id}"
            )

        if any(existing.edge_id == edge.edge_id for existing in self.edges):
            raise ExecutionGraphError(
                f"Edge already exists: {edge.edge_id}"
            )

        if any(
            existing.source_id == edge.source_id
            and existing.target_id == edge.target_id
            for existing in self.edges
        ):
            raise ExecutionGraphError(
                f"Duplicate edge is not allowed: "
                f"{edge.source_id} -> {edge.target_id}"
            )

        self.edges.append(edge)

        if not self._is_acyclic():
            self.edges.pop()
            raise ExecutionGraphError(
                f"Edge would create a cycle: "
                f"{edge.source_id} -> {edge.target_id}"
            )

    def remove_edge(self, edge: ExecutionEdge) -> None:
        if edge in self.edges:
            self.edges.remove(edge)

    def get_edges_from(self, node_id: UUID) -> list[ExecutionEdge]:
        return [
            edge
            for edge in self.edges
            if edge.source_id == node_id
        ]

    def get_edges_to(self, node_id: UUID) -> list[ExecutionEdge]:
        return [
            edge
            for edge in self.edges
            if edge.target_id == node_id
        ]

    # =========================================================
    # Traversal API
    # =========================================================

    def roots(self) -> list[ExecutionNode]:
        targets = {edge.target_id for edge in self.edges}

        return [
            node
            for node in self.nodes.values()
            if node.node_id not in targets
        ]

    def leaves(self) -> list[ExecutionNode]:
        sources = {edge.source_id for edge in self.edges}

        return [
            node
            for node in self.nodes.values()
            if node.node_id not in sources
        ]

    def successors(self, node_id: UUID) -> list[ExecutionNode]:
        return [
            self.nodes[edge.target_id]
            for edge in self.edges
            if edge.source_id == node_id
        ]

    def predecessors(self, node_id: UUID) -> list[ExecutionNode]:
        return [
            self.nodes[edge.source_id]
            for edge in self.edges
            if edge.target_id == node_id
        ]

    # =========================================================
    # Validation
    # =========================================================

    def validate(self) -> None:
        node_ids = set(self.nodes)

        edge_ids: set[UUID] = set()
        edge_pairs: set[tuple[UUID, UUID]] = set()

        for edge in self.edges:
            if edge.edge_id in edge_ids:
                raise ExecutionGraphError(
                    f"Duplicate edge ID: {edge.edge_id}"
                )

            edge_ids.add(edge.edge_id)

            if edge.source_id not in node_ids:
                raise ExecutionGraphError(
                    f"Edge source node does not exist: {edge.source_id}"
                )

            if edge.target_id not in node_ids:
                raise ExecutionGraphError(
                    f"Edge target node does not exist: {edge.target_id}"
                )

            if edge.is_self_loop():
                raise ExecutionGraphError(
                    f"Self-loop is not allowed: {edge.source_id}"
                )

            pair = (edge.source_id, edge.target_id)

            if pair in edge_pairs:
                raise ExecutionGraphError(
                    f"Duplicate edge is not allowed: "
                    f"{edge.source_id} -> {edge.target_id}"
                )

            edge_pairs.add(pair)

        if not self._is_acyclic():
            raise ExecutionGraphError("ExecutionGraph contains a cycle")

    def _is_acyclic(self) -> bool:
        adjacency: dict[UUID, list[UUID]] = {
            node_id: []
            for node_id in self.nodes
        }

        for edge in self.edges:
            if (
                edge.source_id not in adjacency
                or edge.target_id not in adjacency
            ):
                return False

            adjacency[edge.source_id].append(edge.target_id)

        visiting: set[UUID] = set()
        visited: set[UUID] = set()

        def visit(node_id: UUID) -> bool:
            if node_id in visiting:
                return False

            if node_id in visited:
                return True

            visiting.add(node_id)

            for successor in adjacency[node_id]:
                if not visit(successor):
                    return False

            visiting.remove(node_id)
            visited.add(node_id)

            return True

        return all(visit(node_id) for node_id in adjacency)

    # =========================================================
    # Serialization
    # =========================================================

    def to_dict(self) -> dict:
        return {
            "graph_id": str(self.graph_id),
            "nodes": {
                str(node_id): node.to_dict()
                for node_id, node in self.nodes.items()
            },
            "edges": [
                edge.to_dict()
                for edge in self.edges
            ],
        }


__all__ = [
    "ExecutionGraph",
    "ExecutionGraphError",
]

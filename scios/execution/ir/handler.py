from __future__ import annotations
from typing import Any
from scios.execution.ir.opcode import Opcode
from scios.execution.graph.graph import ExecutionGraph
from scios.execution.node.node import ExecutionNode
from scios.execution.graph.edge import ExecutionEdge


class InstructionHandler:
    """
    InstructionHandler = Concrete implementations for opcodes.
    """

    # =========================================================
    # Node operations
    # =========================================================

    def add_node(self, graph: ExecutionGraph, payload: dict[str, Any]) -> ExecutionNode:
        node = ExecutionNode(**payload)
        graph.add_node(node)
        return node

    def remove_node(self, graph: ExecutionGraph, node_id) -> None:
        graph.remove_node(node_id)

    def update_node(self, graph: ExecutionGraph, node_id, payload: dict[str, Any]) -> None:
        node = graph.get_node(node_id)
        if node:
            for k, v in payload.items():
                setattr(node, k, v)

    # =========================================================
    # Edge operations
    # =========================================================

    def add_edge(self, graph: ExecutionGraph, payload: dict[str, Any]) -> ExecutionEdge:
        edge = ExecutionEdge(**payload)
        graph.add_edge(edge)
        return edge

    def remove_edge(self, graph: ExecutionGraph, edge_id) -> None:
        graph.edges = [e for e in graph.edges if str(e.edge_id) != str(edge_id)]

    def update_edge(self, graph: ExecutionGraph, edge_id, payload: dict[str, Any]) -> None:
        for e in graph.edges:
            if str(e.edge_id) == str(edge_id):
                e.metadata.update(payload)

    # =========================================================
    # Execution lifecycle
    # =========================================================

    def start_node(self, graph: ExecutionGraph, node_id) -> None:
        node = graph.get_node(node_id)
        if node:
            node.status = "running"

    def complete_node(self, graph: ExecutionGraph, node_id) -> None:
        node = graph.get_node(node_id)
        if node:
            node.status = "success"

    def fail_node(self, graph: ExecutionGraph, node_id) -> None:
        node = graph.get_node(node_id)
        if node:
            node.status = "failed"

    def retry_node(self, graph: ExecutionGraph, node_id) -> None:
        node = graph.get_node(node_id)
        if node:
            node.status = "retrying"

    def cancel_node(self, graph: ExecutionGraph, node_id) -> None:
        node = graph.get_node(node_id)
        if node:
            node.status = "cancelled"

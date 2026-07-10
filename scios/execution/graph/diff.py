from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from scios.execution.graph.graph import ExecutionGraph


@dataclass
class GraphDiff:
    """
    GraphDiff = Compute differences between two ExecutionGraphs.
    """

    before: ExecutionGraph
    after: ExecutionGraph

    # =========================================================
    # Node diff
    # =========================================================

    def diff_nodes(self) -> Dict[str, Any]:
        before_nodes = set(self.before.nodes.keys())
        after_nodes = set(self.after.nodes.keys())

        added = after_nodes - before_nodes
        removed = before_nodes - after_nodes
        common = before_nodes & after_nodes

        changed = {}
        for nid in common:
            if self.before.nodes[nid].to_dict() != self.after.nodes[nid].to_dict():
                changed[str(nid)] = {
                    "before": self.before.nodes[nid].to_dict(),
                    "after": self.after.nodes[nid].to_dict(),
                }

        return {
            "added": [str(n) for n in added],
            "removed": [str(n) for n in removed],
            "changed": changed,
        }

    # =========================================================
    # Edge diff
    # =========================================================

    def diff_edges(self) -> Dict[str, Any]:
        before_edges = {e.to_dict()["edge_id"]: e.to_dict() for e in self.before.edges}
        after_edges = {e.to_dict()["edge_id"]: e.to_dict() for e in self.after.edges}

        added = set(after_edges.keys()) - set(before_edges.keys())
        removed = set(before_edges.keys()) - set(after_edges.keys())
        common = set(before_edges.keys()) & set(after_edges.keys())

        changed = {}
        for eid in common:
            if before_edges[eid] != after_edges[eid]:
                changed[eid] = {
                    "before": before_edges[eid],
                    "after": after_edges[eid],
                }

        return {
            "added": [after_edges[eid] for eid in added],
            "removed": [before_edges[eid] for eid in removed],
            "changed": changed,
        }

    # =========================================================
    # Full diff
    # =========================================================

    def diff_all(self) -> Dict[str, Any]:
        return {
            "nodes": self.diff_nodes(),
            "edges": self.diff_edges(),
        }

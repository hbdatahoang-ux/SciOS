"""
ExecutionGraph Subsystem
========================

Provides core IR representation for program execution:
- ExecutionGraph: Directed graph of nodes and edges
- ExecutionEdge: Dependency relation between nodes
- GraphRevision: Immutable snapshots of graph state
- GraphHistory: Ordered log of graph changes
- GraphDiff: Differences between two graphs
- GraphChange: Atomic changes and change sets
"""

from scios.execution.graph.graph import ExecutionGraph
from scios.execution.graph.edge import ExecutionEdge
from scios.execution.graph.revision import GraphRevision, GraphRevisionManager
from scios.execution.graph.history import GraphHistory, GraphHistoryEvent
from scios.execution.graph.diff import GraphDiff
from scios.execution.graph.change import GraphChange, GraphChangeSet, GraphChangeApplier

__all__ = [
    "ExecutionGraph",
    "ExecutionEdge",
    "GraphRevision",
    "GraphRevisionManager",
    "GraphHistory",
    "GraphHistoryEvent",
    "GraphDiff",
    "GraphChange",
    "GraphChangeSet",
    "GraphChangeApplier",
]

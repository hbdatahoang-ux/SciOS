from scios.execution.graph.graph import ExecutionGraph
from scios.execution.graph.change.set import GraphChangeSet
from scios.execution.node.node import ExecutionNode
from scios.execution.graph.edge import ExecutionEdge


class GraphChangeApplier:
    """
    GraphChangeApplier = Applies GraphChangeSet to ExecutionGraph.
    """

    def apply(self, graph: ExecutionGraph, change_set: GraphChangeSet) -> ExecutionGraph:
        for change in change_set.changes:
            if change.action == "add_node":
                node = ExecutionNode(**change.payload)
                graph.add_node(node)

            elif change.action == "remove_node":
                graph.remove_node(change.target_id)

            elif change.action == "add_edge":
                edge = ExecutionEdge(**change.payload)
                graph.add_edge(edge)

            elif change.action == "remove_edge":
                # Find edge by ID
                graph.edges = [e for e in graph.edges if str(e.edge_id) != str(change.target_id)]

            elif change.action == "update_metadata":
                node = graph.get_node(change.target_id)
                if node:
                    node.metadata.update(change.payload)

        return graph

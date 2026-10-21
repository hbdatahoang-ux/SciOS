from scios.execution.graph.graph import ExecutionGraph
from scios.execution.node.node import ExecutionNode
from scios.execution.operation.ref import OperationRef


def test_graph_preserves_operation_ref_on_add_and_get():
    ref = OperationRef(
        name="data.analyze",
        version="1.0",
    )

    node = ExecutionNode(
        name="Analyze data",
        operation_ref=ref,
    )

    graph = ExecutionGraph()
    graph.add_node(node)

    stored = graph.get_node(node.node_id)

    assert stored is node
    assert stored.operation_ref == ref


def test_graph_to_dict_preserves_operation_ref():
    ref = OperationRef(
        name="data.analyze",
        version="1.0",
    )

    node = ExecutionNode(
        name="Analyze data",
        operation_ref=ref,
    )

    graph = ExecutionGraph()
    graph.add_node(node)

    payload = graph.to_dict()
    node_payload = payload["nodes"][str(node.node_id)]

    assert node_payload["operation_ref"] == {
        "name": "data.analyze",
        "version": "1.0",
    }

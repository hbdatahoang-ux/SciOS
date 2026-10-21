from scios.cognitive_core.planner import Goal, Plan, Task
from scios.compilation.plan_compiler import PlanCompiler
from scios.execution.operation.ref import OperationRef


class _Binder:
    def __init__(self, refs):
        self.refs = refs

    def bind(self, task):
        return self.refs[task.id]


def test_plan_compiler_preserves_three_node_dependency_graph():
    refs = {
        "a": OperationRef("step.a", "1.0"),
        "b": OperationRef("step.b", "1.0"),
        "c": OperationRef("step.c", "1.0"),
    }

    plan = Plan(
        goal=Goal("Three-step pipeline"),
        tasks=[
            Task("Step A", task_id="a"),
            Task("Step B", task_id="b", dependencies=["a"]),
            Task("Step C", task_id="c", dependencies=["b"]),
        ],
    )

    graph = PlanCompiler(
        operation_binder=_Binder(refs)
    ).compile(plan)

    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2

    nodes = {
        node.metadata["source"]["task_id"]: node
        for node in graph.nodes.values()
    }

    assert nodes["a"].operation_ref == refs["a"]
    assert nodes["b"].operation_ref == refs["b"]
    assert nodes["c"].operation_ref == refs["c"]

    assert [node.node_id for node in graph.roots()] == [
        nodes["a"].node_id
    ]

    assert [node.node_id for node in graph.leaves()] == [
        nodes["c"].node_id
    ]

    assert graph.successors(nodes["a"].node_id) == [nodes["b"]]
    assert graph.successors(nodes["b"].node_id) == [nodes["c"]]
    assert graph.successors(nodes["c"].node_id) == []

    assert graph.predecessors(nodes["a"].node_id) == []
    assert graph.predecessors(nodes["b"].node_id) == [nodes["a"]]
    assert graph.predecessors(nodes["c"].node_id) == [nodes["b"]]

    assert all(
        node.status.value == "ready"
        for node in graph.nodes.values()
    )


def test_three_node_compilation_does_not_execute_operations():
    calls = []

    refs = {
        "a": OperationRef("step.a", "1.0"),
        "b": OperationRef("step.b", "1.0"),
        "c": OperationRef("step.c", "1.0"),
    }

    plan = Plan(
        goal=Goal("No execution during compilation"),
        tasks=[
            Task("Step A", task_id="a"),
            Task("Step B", task_id="b", dependencies=["a"]),
            Task("Step C", task_id="c", dependencies=["b"]),
        ],
    )

    class _RecordingBinder:
        def bind(self, task):
            calls.append(task.id)
            return refs[task.id]

    graph = PlanCompiler(
        operation_binder=_RecordingBinder()
    ).compile(plan)

    assert len(graph.nodes) == 3
    assert calls == ["a", "b", "c"]

    assert all(
        node.status.value == "ready"
        for node in graph.nodes.values()
    )

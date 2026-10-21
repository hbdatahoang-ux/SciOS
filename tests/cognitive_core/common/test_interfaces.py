from __future__ import annotations

import inspect

import pytest

from scios.cognitive_core.common.interfaces import (
    MemoryInterface,
    PlannerInterface,
    ReasonerInterface,
    ToolInterface,
)


# ==========================================================
# PlannerInterface
# ==========================================================


def test_planner_interface_is_abstract():
    assert inspect.isabstract(PlannerInterface)


def test_planner_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        PlannerInterface()


def test_planner_interface_declares_plan():
    assert hasattr(PlannerInterface, "plan")
    assert callable(PlannerInterface.plan)


def test_planner_plan_is_abstract():
    assert getattr(PlannerInterface.plan, "__isabstractmethod__", False)


def test_planner_plan_signature():
    signature = inspect.signature(PlannerInterface.plan)

    parameters = list(signature.parameters.values())

    assert [parameter.name for parameter in parameters] == [
        "self",
        "task",
    ]

    assert signature.return_annotation == "dict[str, Any]"


# ==========================================================
# MemoryInterface
# ==========================================================


def test_memory_interface_is_abstract():
    assert inspect.isabstract(MemoryInterface)


def test_memory_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        MemoryInterface()


def test_memory_interface_declares_store():
    assert hasattr(MemoryInterface, "store")
    assert callable(MemoryInterface.store)


def test_memory_interface_declares_retrieve():
    assert hasattr(MemoryInterface, "retrieve")
    assert callable(MemoryInterface.retrieve)


def test_memory_store_is_abstract():
    assert getattr(MemoryInterface.store, "__isabstractmethod__", False)


def test_memory_retrieve_is_abstract():
    assert getattr(MemoryInterface.retrieve, "__isabstractmethod__", False)


def test_memory_store_signature():
    signature = inspect.signature(MemoryInterface.store)

    parameters = list(signature.parameters.values())

    assert [parameter.name for parameter in parameters] == [
        "self",
        "key",
        "value",
    ]

    assert signature.return_annotation == "None"


def test_memory_retrieve_signature():
    signature = inspect.signature(MemoryInterface.retrieve)

    parameters = list(signature.parameters.values())

    assert [parameter.name for parameter in parameters] == [
        "self",
        "key",
    ]

    assert signature.return_annotation == "Any"


# ==========================================================
# ReasonerInterface
# ==========================================================


def test_reasoner_interface_is_abstract():
    assert inspect.isabstract(ReasonerInterface)


def test_reasoner_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        ReasonerInterface()


def test_reasoner_interface_declares_infer():
    assert hasattr(ReasonerInterface, "infer")
    assert callable(ReasonerInterface.infer)


def test_reasoner_infer_is_abstract():
    assert getattr(ReasonerInterface.infer, "__isabstractmethod__", False)


def test_reasoner_infer_signature():
    signature = inspect.signature(ReasonerInterface.infer)

    parameters = list(signature.parameters.values())

    assert [parameter.name for parameter in parameters] == [
        "self",
        "context",
    ]

    assert signature.return_annotation == "list[str]"


# ==========================================================
# ToolInterface
# ==========================================================


def test_tool_interface_is_protocol():
    assert getattr(ToolInterface, "_is_protocol", False) is True


def test_tool_interface_is_not_abstract():
    assert inspect.isabstract(ToolInterface) is False


def test_tool_interface_declares_call():
    assert hasattr(ToolInterface, "__call__")
    assert callable(ToolInterface.__call__)


def test_tool_interface_call_signature():
    signature = inspect.signature(ToolInterface.__call__)

    parameters = list(signature.parameters.values())

    assert parameters[0].name == "self"

    inputs = parameters[1]

    assert inputs.name == "inputs"
    assert inputs.kind is inspect.Parameter.VAR_KEYWORD


# ==========================================================
# Concrete Implementations
# ==========================================================


class ConcretePlanner(PlannerInterface):
    def plan(self, task):
        return {"task": task}


class ConcreteMemory(MemoryInterface):
    def __init__(self):
        self.data = {}

    def store(self, key, value):
        self.data[key] = value

    def retrieve(self, key):
        return self.data.get(key)


class ConcreteReasoner(ReasonerInterface):
    def infer(self, context):
        return ["inference"]


def test_concrete_planner_satisfies_interface():
    planner = ConcretePlanner()

    assert isinstance(planner, PlannerInterface)
    assert planner.plan("test") == {"task": "test"}


def test_concrete_memory_satisfies_interface():
    memory = ConcreteMemory()

    assert isinstance(memory, MemoryInterface)

    memory.store("key", "value")

    assert memory.retrieve("key") == "value"


def test_concrete_reasoner_satisfies_interface():
    reasoner = ConcreteReasoner()

    assert isinstance(reasoner, ReasonerInterface)
    assert reasoner.infer({}) == ["inference"]


# ==========================================================
# Missing Abstract Methods
# ==========================================================


def test_incomplete_planner_remains_abstract():
    class IncompletePlanner(PlannerInterface):
        pass

    assert inspect.isabstract(IncompletePlanner)

    with pytest.raises(TypeError):
        IncompletePlanner()


def test_incomplete_memory_remains_abstract():
    class IncompleteMemory(MemoryInterface):
        def store(self, key, value):
            pass

    assert inspect.isabstract(IncompleteMemory)

    with pytest.raises(TypeError):
        IncompleteMemory()


def test_incomplete_reasoner_remains_abstract():
    class IncompleteReasoner(ReasonerInterface):
        pass

    assert inspect.isabstract(IncompleteReasoner)

    with pytest.raises(TypeError):
        IncompleteReasoner()


# ==========================================================
# Tool Structural Compatibility
# ==========================================================


def test_callable_is_structurally_compatible_with_tool_interface():
    class ExampleTool:
        def __call__(self, **inputs):
            return inputs

    tool = ExampleTool()

    assert callable(tool)
    assert tool(name="test") == {"name": "test"}


def test_function_is_compatible_with_tool_contract():
    def tool(**inputs):
        return inputs

    assert callable(tool)
    assert tool(value=42) == {"value": 42}


# ==========================================================
# Interface Separation
# ==========================================================


def test_interfaces_are_distinct_types():
    interfaces = {
        PlannerInterface,
        MemoryInterface,
        ReasonerInterface,
        ToolInterface,
    }

    assert len(interfaces) == 4


def test_planner_does_not_inherit_from_other_interfaces():
    assert not issubclass(PlannerInterface, MemoryInterface)
    assert not issubclass(PlannerInterface, ReasonerInterface)


def test_memory_does_not_inherit_from_other_interfaces():
    assert not issubclass(MemoryInterface, PlannerInterface)
    assert not issubclass(MemoryInterface, ReasonerInterface)


def test_reasoner_does_not_inherit_from_other_interfaces():
    assert not issubclass(ReasonerInterface, PlannerInterface)
    assert not issubclass(ReasonerInterface, MemoryInterface)


# ==========================================================
# Public Contract
# ==========================================================


def test_interface_public_names():
    assert PlannerInterface.__name__ == "PlannerInterface"
    assert MemoryInterface.__name__ == "MemoryInterface"
    assert ReasonerInterface.__name__ == "ReasonerInterface"
    assert ToolInterface.__name__ == "ToolInterface"
from scios.agents.executor import AgentExecutor
from scios.cognitive_core.memory import (
    EpisodicMemory,
    KeywordRetrieval,
    MemoryManager,
    SemanticMemory,
    WorkingMemory,
)
from scios.cognitive_core.reasoning.core import (
    ReasoningProblem,
    ReasoningResult,
)
from scios.cognitive_core.reasoning.engine import ReasoningEngine


def make_executor() -> AgentExecutor:
    memory = MemoryManager(
        working=WorkingMemory(),
        episodic=EpisodicMemory(),
        semantic=SemanticMemory(),
    )
    return AgentExecutor(
        memory=memory,
        reasoning=ReasoningEngine(),
    )


def test_constructor_accepts_canonical_dependencies() -> None:
    executor = make_executor()

    assert isinstance(executor.memory, MemoryManager)
    assert isinstance(executor.reasoning, ReasoningEngine)


def test_execute_uses_canonical_reasoning_contract() -> None:
    executor = make_executor()

    result = executor.execute("test task")

    assert isinstance(result["reasoning"], ReasoningResult)
    assert isinstance(result["reasoning"].problem, ReasoningProblem)


def test_reasoning_problem_preserves_task() -> None:
    executor = make_executor()

    result = executor.execute("test task")

    reasoning = result["reasoning"]

    assert reasoning.problem.query == "test task"


def test_reasoning_result_contains_memory_context() -> None:
    executor = make_executor()

    result = executor.execute("test task")

    reasoning = result["reasoning"]

    assert isinstance(reasoning.problem.context, dict)


def test_memory_retrieval_uses_keyword_strategy() -> None:
    executor = make_executor()

    record = executor.memory.semantic.store(
        __import__(
            "scios.cognitive_core.memory",
            fromlist=["MemoryRecord"],
        ).MemoryRecord(content="test task information")
    )

    retrieved = executor.memory.retrieve(
        KeywordRetrieval(),
        "test task",
        __import__(
            "scios.cognitive_core.memory",
            fromlist=["MemoryKind"],
        ).MemoryKind.SEMANTIC,
    )

    assert record in retrieved


def test_execute_preserves_existing_output_contract() -> None:
    executor = make_executor()

    result = executor.execute("test task")

    assert set(result) == {
        "task",
        "plan",
        "memory",
        "reasoning",
        "tools",
        "reflection",
        "response",
    }


def test_execute_preserves_task() -> None:
    executor = make_executor()

    result = executor.execute("hello")

    assert result["task"] == "hello"


def test_call_delegates_to_execute() -> None:
    executor = make_executor()

    result = executor("hello")

    assert result["task"] == "hello"


def test_status_contract() -> None:
    executor = make_executor()

    status = executor.status()

    assert set(status) == {
        "memory",
        "reasoning",
        "planner",
        "tooluse",
        "reflection",
    }


def test_repr_contract() -> None:
    executor = make_executor()

    value = repr(executor)

    assert value.startswith("AgentExecutor(")
    assert "MemoryManager" in value
    assert "ReasoningEngine" in value

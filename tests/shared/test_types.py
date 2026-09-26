"""
Tests for SciOS shared type contracts.
"""

from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import MutableMapping
from collections.abc import Sequence
from typing import Any
from typing import get_args
from typing import get_origin

from scios.shared.types import (
    AgentState,
    Callback,
    ConfigDict,
    Embedding,
    Embeddings,
    Event,
    EventName,
    Executable,
    Identifiable,
    Initializable,
    KernelState,
    Metadata,
    Named,
    PipelineState,
    RuntimeState,
    Serializable,
    Shutdownable,
    Task,
    TaskID,
    TaskResult,
)


# ============================================================================
# Type aliases
# ============================================================================


def test_type_aliases_exist():
    aliases = (
        ConfigDict,
        Metadata,
        TaskID,
        Task,
        TaskResult,
        Embedding,
        Embeddings,
        EventName,
        Event,
        Callback,
    )

    assert all(alias is not None for alias in aliases)


def test_mapping_aliases_have_expected_origins():
    assert get_origin(ConfigDict) is dict
    assert get_args(ConfigDict) == (str, Any)

    assert get_origin(Metadata) is dict
    assert get_args(Metadata) == (str, Any)


def test_scalar_aliases_have_expected_origins():
    assert TaskID is str
    assert EventName is str


def test_task_alias_has_expected_structure():
    args = get_args(Task)

    assert str in args
    assert get_origin(args[1]) is Mapping


def test_embedding_alias_has_expected_structure():
    assert get_origin(Embedding) is Sequence
    assert get_args(Embedding) == (float,)


def test_embeddings_alias_has_expected_structure():
    assert get_origin(Embeddings) is Sequence
    assert get_args(Embeddings) == (Embedding,)


def test_event_alias_has_expected_structure():
    assert get_origin(Event) is Mapping
    assert get_args(Event) == (str, Any)


def test_task_result_alias_has_expected_structure():
    assert get_origin(TaskResult) is MutableMapping
    assert get_args(TaskResult) == (str, Any)


def test_callback_alias_is_callable():
    assert get_origin(Callback) is Callable


# ============================================================================
# State literals
# ============================================================================


def test_state_literals_exist():
    states = (
        KernelState,
        RuntimeState,
        PipelineState,
        AgentState,
    )

    assert all(state is not None for state in states)


def test_kernel_state_values():
    assert KernelState.__args__ == (
        "created",
        "booting",
        "running",
        "stopping",
        "stopped",
        "failed",
    )


def test_runtime_state_values():
    assert RuntimeState.__args__ == (
        "created",
        "idle",
        "running",
        "completed",
        "failed",
    )


def test_pipeline_state_values():
    assert PipelineState.__args__ == (
        "created",
        "running",
        "completed",
        "failed",
    )


def test_agent_state_values():
    assert AgentState.__args__ == (
        "idle",
        "planning",
        "running",
        "waiting",
        "reflecting",
        "finished",
        "failed",
    )


# ============================================================================
# Protocols
# ============================================================================


def test_protocols_exist():
    protocols = (
        Executable,
        Serializable,
        Identifiable,
        Named,
        Initializable,
        Shutdownable,
    )

    assert all(protocol is not None for protocol in protocols)


def test_protocols_are_protocols():
    protocols = (
        Executable,
        Serializable,
        Identifiable,
        Named,
        Initializable,
        Shutdownable,
    )

    for protocol in protocols:
        assert getattr(protocol, "_is_protocol", False) is True


def test_protocols_are_runtime_checkable():
    protocols = (
        Executable,
        Serializable,
        Identifiable,
        Named,
        Initializable,
        Shutdownable,
    )

    for protocol in protocols:
        assert getattr(
            protocol,
            "_is_runtime_protocol",
            False,
        ) is True


# ============================================================================
# Executable
# ============================================================================


def test_executable_protocol_accepts_matching_object():
    class Example:
        def execute(self, *args, **kwargs):
            return None

    assert isinstance(Example(), Executable)


def test_executable_protocol_rejects_non_matching_object():
    class Example:
        pass

    assert not isinstance(Example(), Executable)


# ============================================================================
# Serializable
# ============================================================================


def test_serializable_protocol_accepts_matching_object():
    class Example:
        def to_dict(self):
            return {}

    assert isinstance(Example(), Serializable)


def test_serializable_protocol_rejects_non_matching_object():
    class Example:
        pass

    assert not isinstance(Example(), Serializable)


# ============================================================================
# Identifiable
# ============================================================================


def test_identifiable_protocol_accepts_matching_object():
    class Example:
        @property
        def id(self) -> str:
            return "example-id"

    obj = Example()

    assert isinstance(obj, Identifiable)
    assert obj.id == "example-id"


def test_identifiable_protocol_rejects_non_matching_object():
    class Example:
        pass

    assert not isinstance(Example(), Identifiable)


# ============================================================================
# Named
# ============================================================================


def test_named_protocol_accepts_matching_object():
    class Example:
        @property
        def name(self) -> str:
            return "example"

    obj = Example()

    assert isinstance(obj, Named)
    assert obj.name == "example"


def test_named_protocol_rejects_non_matching_object():
    class Example:
        pass

    assert not isinstance(Example(), Named)


# ============================================================================
# Initializable
# ============================================================================


def test_initializable_protocol_accepts_matching_object():
    class Example:
        def initialize(self) -> None:
            return None

    assert isinstance(Example(), Initializable)


def test_initializable_protocol_rejects_non_matching_object():
    class Example:
        pass

    assert not isinstance(Example(), Initializable)


# ============================================================================
# Shutdownable
# ============================================================================


def test_shutdownable_protocol_accepts_matching_object():
    class Example:
        def shutdown(self) -> None:
            return None

    assert isinstance(Example(), Shutdownable)


def test_shutdownable_protocol_rejects_non_matching_object():
    class Example:
        pass

    assert not isinstance(Example(), Shutdownable)


# ============================================================================
# Structural protocol independence
# ============================================================================


def test_object_can_implement_multiple_protocols():
    class Example:
        @property
        def id(self) -> str:
            return "id"

        @property
        def name(self) -> str:
            return "name"

        def execute(self, *args, **kwargs):
            return None

        def to_dict(self):
            return {}

        def initialize(self) -> None:
            return None

        def shutdown(self) -> None:
            return None

    obj = Example()

    assert isinstance(obj, Executable)
    assert isinstance(obj, Serializable)
    assert isinstance(obj, Identifiable)
    assert isinstance(obj, Named)
    assert isinstance(obj, Initializable)
    assert isinstance(obj, Shutdownable)


# ============================================================================
# Runtime examples
# ============================================================================


def test_task_accepts_string():
    value: Task = "scientific task"

    assert isinstance(value, str)


def test_task_accepts_mapping():
    value: Task = {
        "name": "scientific task",
        "priority": 1,
    }

    assert isinstance(value, Mapping)


def test_embedding_is_sequence_of_floats():
    value: Embedding = [0.1, 0.2, 0.3]

    assert isinstance(value, list)
    assert all(isinstance(item, float) for item in value)


def test_embeddings_is_sequence_of_embeddings():
    value: Embeddings = [
        [0.1, 0.2],
        [0.3, 0.4],
    ]

    assert len(value) == 2
    assert all(isinstance(item, list) for item in value)
    assert all(
        all(isinstance(item, float) for item in embedding)
        for embedding in value
    )


def test_event_is_mapping():
    value: Event = {
        "event": "runtime.task.started",
        "task_id": "task-1",
    }

    assert isinstance(value, Mapping)


def test_callback_is_callable():
    def callback(value):
        return value

    cb: Callback = callback

    assert callable(cb)
    assert cb("ok") == "ok"


def test_task_result_is_mutable_mapping():
    value: TaskResult = {
        "status": "completed",
    }

    value["result"] = 42

    assert value["status"] == "completed"
    assert value["result"] == 42
